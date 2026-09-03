// unyts/graph.cpp — UDigraph implementation + BFS/DFS/lean_BFS/hybrid_BFS.
//
// Faithfully ports Python network.py (UNode, UDigraph, Conversion) and
// searches.py (BFS, DFS, lean_BFS, hybrid_BFS) to C++17.

#include "unyts/graph.hpp"

#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <deque>
#include <functional>
#include <memory>
#include <mutex>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <unordered_map>
#include <unordered_set>

namespace unyts {

// ─── Conversion::get_convert ─────────────────────────────────────────────────
// Mirrors Python Conversion.get_convert():
//   if rev → return lambda that computes  x / conv(1)
//   else   → return conv directly

ConvFn Conversion::get_convert() const {
    if (rev && conv) {
        // capture by value so the lambda owns a copy of conv
        ConvFn fn_copy = conv;
        return [fn_copy](double x) { return x / fn_copy(1.0); };
    }
    return conv;
}

// ─── UDigraph — static member ─────────────────────────────────────────────────
const std::vector<EdgeEntry> UDigraph::empty_edges_{};

// ─── UDigraph::add_node ───────────────────────────────────────────────────────
void UDigraph::add_node(const UNode& node) {
    // Silently ignore duplicates (mirrors Python behaviour)
    if (nodes_.count(node.name)) return;
    nodes_.emplace(node.name, node);
    edges_.emplace(node.name, std::vector<EdgeEntry>{});
}

// ─── UDigraph::add_edge ───────────────────────────────────────────────────────
void UDigraph::add_edge(const Conversion& edge) {
    const std::string& src_name  = edge.src.name;
    const std::string& dest_name = edge.dest.name;

    if (!nodes_.count(src_name) || !nodes_.count(dest_name)) {
        throw std::invalid_argument(
            "add_edge: node not in graph (" + src_name + " -> " + dest_name + ")");
    }

    auto& outgoing = edges_.at(src_name);

    // Avoid duplicate edges (same dest name)
    for (const auto& e : outgoing) {
        if (e.dest.name == dest_name) return;
    }

    outgoing.push_back(EdgeEntry{ edge.dest, edge.get_convert() });
}

// ─── UDigraph::has_node ───────────────────────────────────────────────────────
bool UDigraph::has_node(const UNode& node) const {
    return nodes_.count(node.name) > 0;
}
bool UDigraph::has_node(const std::string& name) const {
    return nodes_.count(name) > 0;
}

// ─── UDigraph::get_node ───────────────────────────────────────────────────────
const UNode* UDigraph::get_node(const std::string& name) const {
    auto it = nodes_.find(name);
    return (it == nodes_.end()) ? nullptr : &it->second;
}

// ─── UDigraph::list_nodes ────────────────────────────────────────────────────
std::vector<std::string> UDigraph::list_nodes() const {
    std::vector<std::string> result;
    result.reserve(nodes_.size());
    for (const auto& kv : nodes_) result.push_back(kv.first);
    return result;
}

// ─── UDigraph::children_of ───────────────────────────────────────────────────
const std::vector<EdgeEntry>& UDigraph::children_of(const UNode& node) const {
    auto it = edges_.find(node.name);
    return (it == edges_.end()) ? empty_edges_ : it->second;
}

// ─── UDigraph::convert ───────────────────────────────────────────────────────
double UDigraph::convert(double value,
                         const UNode& src, const UNode& dest) const {
    const auto& outgoing = children_of(src);
    for (const auto& e : outgoing) {
        if (e.dest == dest) return e.fn(value);
    }
    throw std::out_of_range(
        "No direct edge from '" + src.name + "' to '" + dest.name + "'");
}

double UDigraph::convert(double value,
                         const std::string& src, const std::string& dest) const {
    const UNode* s = get_node(src);
    const UNode* d = get_node(dest);
    if (!s || !d) throw std::out_of_range("Node not in graph");
    return convert(value, *s, *d);
}

// ─── UDigraph::conversion ────────────────────────────────────────────────────
ConvFn UDigraph::conversion(const UNode& src, const UNode& dest) const {
    const auto& outgoing = children_of(src);
    for (const auto& e : outgoing) {
        if (e.dest == dest) return e.fn;
    }
    throw std::out_of_range(
        "No direct edge from '" + src.name + "' to '" + dest.name + "'");
}

// ─── Search memory ────────────────────────────────────────────────────────────
bool UDigraph::has_memory(const std::string& key) const {
    return memory_.count(key) > 0;
}
void UDigraph::set_memory(const std::string& key, const NodeNamePath& path) {
    memory_[key] = path;
}
const NodeNamePath* UDigraph::get_memory(const std::string& key) const {
    auto it = memory_.find(key);
    return (it == memory_.end()) ? nullptr : &it->second;
}
void UDigraph::clean_memory() {
    memory_.clear();
}

// ─── UDigraph::str ────────────────────────────────────────────────────────────
std::string UDigraph::str() const {
    std::ostringstream oss;
    for (const auto& kv : edges_) {
        for (const auto& e : kv.second) {
            oss << kv.first << "->" << e.dest.name << "\n";
        }
    }
    return oss.str();
}

// ─── get_descendants ─────────────────────────────────────────────────────────
// BFS up to max_depth hops from start_name.
// Returns the set of all reachable node names (not including start_name itself
// unless there is a cycle back).
// Mirrors Python converter._get_descendants() for the purposes of lean_BFS
// pruning (simplified: doesn't handle combined unit strings).

std::unordered_set<std::string> get_descendants(
    const UDigraph& g,
    const std::string& start_name,
    int max_depth)
{
    std::unordered_set<std::string> visited;
    if (!g.has_node(start_name)) return visited;

    // BFS with depth tracking: queue entries are {node_name, depth}
    std::queue<std::pair<std::string, int>> q;
    q.push({start_name, 0});

    while (!q.empty()) {
        auto [name, depth] = q.front();
        q.pop();
        if (visited.count(name)) continue;
        visited.insert(name);
        if (depth >= max_depth) continue;
        const UNode* node = g.get_node(name);
        if (!node) continue;
        for (const EdgeEntry& e : g.children_of(*node)) {
            if (!visited.count(e.dest.name)) {
                q.push({e.dest.name, depth + 1});
            }
        }
    }
    visited.erase(start_name); // exclude the start node itself
    return visited;
}

// ─── BFS ─────────────────────────────────────────────────────────────────────
// Faithful port of Python BFS (searches.py):
//   - Maintains a queue of paths (vectors of UNodes)
//   - Skips nodes that have already been visited (visited_nodes set)
//   - For each frontier node, extends only with children not already in the
//     current path (prevents immediate cycles)
//   - Returns as soon as end is reached; nullopt on timeout or exhaustion

std::optional<Path> BFS(const UDigraph& g,
                        const UNode& start, const UNode& end,
                        TimePoint deadline, bool /*verbose*/,
                        const std::atomic<bool>* stop) {
    if (start == end) return Path{start};

    // path_queue: each entry is a complete path from start to some node
    std::queue<Path> path_queue;
    path_queue.push(Path{start});

    std::unordered_set<std::string> visited;

    while (!path_queue.empty()) {
        // Timeout / cancellation check
        if (Clock::now() > deadline) return std::nullopt;
        if (stop && stop->load(std::memory_order_relaxed)) return std::nullopt;

        Path conv_path = std::move(path_queue.front());
        path_queue.pop();

        const UNode& last_node = conv_path.back();

        // Skip if already visited from a different (shorter) path
        if (visited.count(last_node.name)) continue;
        visited.insert(last_node.name);

        // Goal test
        if (last_node == end) return conv_path;

        // Expand: add children not already in the current path
        for (const EdgeEntry& edge : g.children_of(last_node)) {
            bool in_path = false;
            for (const UNode& n : conv_path) {
                if (n == edge.dest) { in_path = true; break; }
            }
            if (!in_path) {
                Path new_path = conv_path;        // copy
                new_path.push_back(edge.dest);
                path_queue.push(std::move(new_path));
            }
        }
    }
    return std::nullopt; // not reachable
}

// ─── DFS ─────────────────────────────────────────────────────────────────────
// Depth-first search.  When branch_depth > 0, a child branch is only explored
// if `end` is reachable from that child within branch_depth hops (pruning via
// get_descendants), mirroring the Python DFS behaviour.

namespace {

// Recursive helper; returns the path if found, std::nullopt otherwise.
std::optional<Path> dfs_impl(const UDigraph& g,
                              const UNode& current,
                              const UNode& end,
                              std::unordered_set<std::string>& visited,
                              Path& current_path,
                              TimePoint deadline,
                              int branch_depth) {
    visited.insert(current.name);

    for (const EdgeEntry& edge : g.children_of(current)) {
        if (Clock::now() > deadline) return std::nullopt;
        if (visited.count(edge.dest.name)) continue;

        // Optional pruning: skip branch if end is not reachable from dest
        if (branch_depth > 0) {
            auto desc = get_descendants(g, edge.dest.name, branch_depth);
            if (!desc.count(end.name) && edge.dest != end) continue;
        }

        current_path.push_back(edge.dest);
        if (edge.dest == end) return current_path;

        auto result = dfs_impl(g, edge.dest, end, visited,
                               current_path, deadline, branch_depth);
        if (result) return result;

        current_path.pop_back();
    }
    return std::nullopt;
}

} // anonymous namespace

std::optional<Path> DFS(const UDigraph& g,
                        const UNode& start, const UNode& end,
                        TimePoint deadline, bool /*verbose*/,
                        int branch_depth) {
    if (start == end) return Path{start};
    std::unordered_set<std::string> visited;
    Path path{start};
    return dfs_impl(g, start, end, visited, path, deadline, branch_depth);
}

// ─── lean_BFS ────────────────────────────────────────────────────────────────
// Builds a slimmed subgraph from the intersection of:
//   - nodes reachable from start (within max_generations hops)
//   - nodes that can reach end   (within max_generations hops in reverse)
// Then runs BFS on that smaller graph.
//
// The Python version iterates a progression of generation counts to find
// the smallest subgraph that still connects start and end.

std::optional<Path> lean_BFS(const UDigraph& g,
                             const UNode& start, const UNode& end,
                             TimePoint deadline, bool verbose,
                             int max_generations,
                             const std::atomic<bool>* stop) {
    // Generation sequence from Python lean_BFS
    static const int gen_steps[] = {0,1,2,3,4,5,7,10,13,16,20,25,30,40,50};
    std::unordered_set<std::string> selection;
    int used_gen = max_generations;

    for (int gen : gen_steps) {
        if (gen > max_generations) break;
        int hops = gen + 1;
        auto start_desc = get_descendants(g, start.name, hops);
        auto end_desc   = get_descendants(g, end.name,   hops);
        // intersection
        selection.clear();
        for (const auto& s : start_desc) {
            if (end_desc.count(s)) selection.insert(s);
        }
        if (!selection.empty()) { used_gen = hops; break; }
    }

    if (selection.empty()) {
        // Fall back to full BFS
        return BFS(g, start, end, deadline, verbose, stop);
    }

    // Also include start and end themselves
    selection.insert(start.name);
    selection.insert(end.name);

    // Build the slimmed graph (just references into g, no deep copies)
    // We represent it by filtering children_of on the fly.
    // Since we can't easily instantiate a new UDigraph without copying nodes,
    // we run BFS with an extra filter: only traverse to nodes in `selection`.

    // Filtered BFS
    if (start == end) return Path{start};

    std::queue<Path> path_queue;
    path_queue.push(Path{start});
    std::unordered_set<std::string> visited;

    while (!path_queue.empty()) {
        if (Clock::now() > deadline) return std::nullopt;
        if (stop && stop->load(std::memory_order_relaxed)) return std::nullopt;

        Path conv_path = std::move(path_queue.front());
        path_queue.pop();

        const UNode& last_node = conv_path.back();
        if (visited.count(last_node.name)) continue;
        visited.insert(last_node.name);
        if (last_node == end) return conv_path;

        for (const EdgeEntry& edge : g.children_of(last_node)) {
            // Only traverse to nodes that are in the slim selection
            if (!selection.count(edge.dest.name)) continue;

            bool in_path = false;
            for (const UNode& n : conv_path) {
                if (n == edge.dest) { in_path = true; break; }
            }
            if (!in_path) {
                Path new_path = conv_path;
                new_path.push_back(edge.dest);
                path_queue.push(std::move(new_path));
            }
        }
    }
    return std::nullopt;
}

// ─── hybrid_BFS ──────────────────────────────────────────────────────────────
// Races BFS and lean_BFS on two long-lived worker threads, taking whichever
// finds a path first and cancelling the other via a shared stop flag (both
// algorithms poll it once per loop iteration).
//
// The previous implementation spawned two brand-new std::async threads on
// *every* call and never cancelled the loser (its std::future destructor
// just blocked until it finished on its own). A full conversion run makes
// hundreds of such calls, so that was hundreds of raw OS thread creations in
// a tight loop -- combined with unyts_capi.dll's thread-attach notifications,
// that reliably hung/starved on Windows. Two dedicated persistent workers
// bound thread creation to a constant 2 for the process lifetime, and the
// stop flag lets the loser bail out almost immediately once a winner is
// found instead of running to its own deadline.

namespace {

// A single-worker FIFO job queue: a persistent thread that pops and runs
// std::function<void()> tasks, blocking when idle.
class JobQueue {
public:
    JobQueue() {
        // Runs for the lifetime of the process; the queue itself is a
        // function-local static (see bfs_queue()/lean_queue() below), so
        // there is no shutdown path -- the thread is simply detached.
        std::thread(&JobQueue::run, this).detach();
    }

    void push(std::function<void()> job) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            queue_.push_back(std::move(job));
        }
        cv_.notify_one();
    }

private:
    void run() {
        for (;;) {
            std::function<void()> job;
            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait(lock, [this] { return !queue_.empty(); });
                job = std::move(queue_.front());
                queue_.pop_front();
            }
            job();
        }
    }

    std::mutex                          mutex_;
    std::condition_variable             cv_;
    std::deque<std::function<void()>>   queue_;
};

JobQueue& bfs_worker()  { static JobQueue* q = new JobQueue(); return *q; }
JobQueue& lean_worker() { static JobQueue* q = new JobQueue(); return *q; }

// Shared result slot for one hybrid_BFS race: each worker fills in its slot
// and notifies; the waiter wakes immediately instead of polling on a timer
// (a poll-and-sleep loop was tried first but Windows' default ~15ms timer
// resolution made every single-digit-microsecond conversion cost ~12ms).
struct RaceState {
    std::mutex              mutex;
    std::condition_variable cv;
    bool                    lean_done = false;
    bool                    bfs_done  = false;
    std::optional<Path>     lean_result;
    std::optional<Path>     bfs_result;
};

} // anonymous namespace

std::optional<Path> hybrid_BFS(const UDigraph& g,
                               const UNode& start, const UNode& end,
                               TimePoint deadline, bool verbose,
                               int max_generations) {
    auto stop  = std::make_shared<std::atomic<bool>>(false);
    auto state = std::make_shared<RaceState>();

    // `g` is always unyts::global_graph(), a static-storage-duration object,
    // so capturing it by reference is safe even if a job outlives this call
    // (the deadline-exceeded path below can return before a job finishes).
    lean_worker().push([&g, start, end, deadline, verbose, max_generations, stop, state] {
        auto result = lean_BFS(g, start, end, deadline, verbose, max_generations, stop.get());
        {
            std::lock_guard<std::mutex> lock(state->mutex);
            state->lean_result = std::move(result);
            state->lean_done   = true;
        }
        state->cv.notify_all();
    });
    bfs_worker().push([&g, start, end, deadline, verbose, stop, state] {
        auto result = BFS(g, start, end, deadline, verbose, stop.get());
        {
            std::lock_guard<std::mutex> lock(state->mutex);
            state->bfs_result = std::move(result);
            state->bfs_done   = true;
        }
        state->cv.notify_all();
    });

    std::unique_lock<std::mutex> lock(state->mutex);
    for (;;) {
        if (state->lean_done) {
            if (state->lean_result) { stop->store(true); return state->lean_result; }
            // lean_BFS found nothing; still need BFS's answer (bounded by
            // the same deadline via wait_until below).
            if (state->cv.wait_until(lock, deadline, [&] { return state->bfs_done; }))
                return state->bfs_result;
            stop->store(true);
            return std::nullopt;
        }
        if (state->bfs_done) {
            if (state->bfs_result) { stop->store(true); return state->bfs_result; }
            if (state->cv.wait_until(lock, deadline, [&] { return state->lean_done; }))
                return state->lean_result;
            stop->store(true);
            return std::nullopt;
        }
        if (!state->cv.wait_until(lock, deadline,
                [&] { return state->lean_done || state->bfs_done; })) {
            stop->store(true); // deadline reached, neither side finished
            return std::nullopt;
        }
    }
}

// ─── apply_path ───────────────────────────────────────────────────────────────
// Apply a path of nodes to an initial value by chaining each direct-edge
// conversion in sequence.

double apply_path(const UDigraph& g, const Path& path, double value) {
    for (size_t i = 0; i + 1 < path.size(); ++i) {
        value = g.convert(value, path[i], path[i + 1]);
    }
    return value;
}

// ─── path_to_string ───────────────────────────────────────────────────────────
std::string path_to_string(const Path& path) {
    if (path.empty()) return "";
    std::ostringstream oss;
    oss << path[0].name;
    for (size_t i = 1; i < path.size(); ++i) {
        oss << " -> " << path[i].name;
    }
    return oss.str();
}

} // namespace unyts
