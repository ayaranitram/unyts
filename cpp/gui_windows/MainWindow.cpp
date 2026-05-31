// gui_windows/MainWindow.cpp — Qt 6 unit-converter window

#include "MainWindow.h"

#include <QApplication>
#include <QAction>
#include <QCompleter>
#include <QDesktopServices>
#include <QDialogButtonBox>
#include <QDoubleSpinBox>
#include <QElapsedTimer>
#include <QEvent>
#include <QGridLayout>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QInputDialog>
#include <QKeyEvent>
#include <QLabel>
#include <QMenuBar>
#include <QMessageBox>
#include <QSortFilterProxyModel>
#include <QSpinBox>
#include <QStatusBar>
#include <QStringListModel>
#include <QTimer>
#include <QUrl>
#include <QVBoxLayout>
#include <QWidget>

#include <cmath>
#include <optional>

// unyts C++ core
#include "unyts/converter.hpp"
#include "unyts/database.hpp"
#include "unyts/aliases.hpp"

// ─────────────────────────────────────────────────────────────────────────────
MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    setWindowTitle("Unyts Converter");
    setWindowIcon(QIcon(":/unyts_icon.ico"));
    setFixedSize(325, 235);  // match Python tkinter GUI (win32: 325×235, non-resizable)

    populateUnits();
    buildUi();
    buildMenus();

    connect(&marqueeTimer_, &QTimer::timeout, this, &MainWindow::onMarqueeTick);
}

// ─────────────────────────────────────────────────────────────────────────────
void MainWindow::populateUnits()
{
    // Initialise the global graph (fast after first call — uses in-process singleton)
    unyts::global_graph();

    const auto names = unyts::all_unit_names();
    allUnits_.reserve(static_cast<int>(names.size()));
    for (const auto& n : names)
        allUnits_ << QString::fromStdString(n);
    allUnits_.sort(Qt::CaseInsensitive);
}

// ─────────────────────────────────────────────────────────────────────────────
void MainWindow::buildUi()
{
    auto* central = new QWidget(this);
    setCentralWidget(central);

    auto* vbox = new QVBoxLayout(central);
    vbox->setContentsMargins(10, 10, 10, 10);
    vbox->setSpacing(6);

    // ── Title ────────────────────────────────────────────────────────────────
    auto* titleLbl = new QLabel("Unyts converter", central);
    {
        QFont f = titleLbl->font();
        f.setPointSize(14);
        f.setBold(true);
        titleLbl->setFont(f);
        titleLbl->setAlignment(Qt::AlignHCenter);
    }
    vbox->addWidget(titleLbl);

    // ── Input grid ───────────────────────────────────────────────────────────
    auto* grid = new QGridLayout();
    grid->setHorizontalSpacing(6);
    grid->setVerticalSpacing(4);

    // Column headers
    auto makeHdr = [&](const QString& text) {
        auto* l = new QLabel(text, central);
        QFont f = l->font(); f.setBold(true); l->setFont(f);
        l->setAlignment(Qt::AlignHCenter);
        return l;
    };
    grid->addWidget(makeHdr("unit"),  0, 1);
    grid->addWidget(makeHdr("value"), 0, 2);

    // "from" row
    grid->addWidget(new QLabel("from", central), 1, 0);
    fromUnitEdit_  = new QLineEdit(central);
    fromValueEdit_ = new QLineEdit(central);
    fromUnitEdit_->setPlaceholderText("unit…");
    fromValueEdit_->setPlaceholderText("value…");
    grid->addWidget(fromUnitEdit_,  1, 1);
    grid->addWidget(fromValueEdit_, 1, 2);

    // "to" row
    grid->addWidget(new QLabel("to", central), 2, 0);
    toUnitEdit_  = new QLineEdit(central);
    toValueEdit_ = new QLineEdit(central);
    toUnitEdit_->setPlaceholderText("unit…");
    toValueEdit_->setPlaceholderText("value…");
    grid->addWidget(toUnitEdit_,  2, 1);
    grid->addWidget(toValueEdit_, 2, 2);

    vbox->addLayout(grid);

    // ── Completers ────────────────────────────────────────────────────────────
    auto makeCompleter = [&](QLineEdit* edit) {
        auto* model     = new QStringListModel(allUnits_, this);
        auto* proxy     = new QSortFilterProxyModel(this);
        proxy->setSourceModel(model);
        proxy->setFilterCaseSensitivity(Qt::CaseInsensitive);
        auto* comp = new QCompleter(proxy, this);
        comp->setCaseSensitivity(Qt::CaseInsensitive);
        comp->setCompletionMode(QCompleter::PopupCompletion);
        comp->setMaxVisibleItems(10);
        edit->setCompleter(comp);
        return comp;
    };
    fromCompleter_ = makeCompleter(fromUnitEdit_);
    toCompleter_   = makeCompleter(toUnitEdit_);

    // ── Convert button ───────────────────────────────────────────────────────
    convertBtn_ = new QPushButton("convert", central);
    convertBtn_->setDefault(true);
    vbox->addWidget(convertBtn_, 0, Qt::AlignHCenter);
    connect(convertBtn_, &QPushButton::clicked, this, &MainWindow::onConvert);

    // ── Repeat search checkbox ───────────────────────────────────────────────
    repeatSearch_ = new QCheckBox("repeat search", central);
    vbox->addWidget(repeatSearch_, 0, Qt::AlignHCenter);

    // ── Status label (timing / errors) ───────────────────────────────────────
    statusLbl_ = new QLabel("", central);
    statusLbl_->setAlignment(Qt::AlignHCenter);
    vbox->addWidget(statusLbl_);

    // ── Path row (hidden by default) ─────────────────────────────────────────
    pathRow_ = new QWidget(central);
    auto* pathRowLayout = new QHBoxLayout(pathRow_);
    pathRowLayout->setContentsMargins(0, 0, 0, 0);
    pathLbl_ = new QLabel("", pathRow_);
    {
        QFont f = pathLbl_->font();
        f.setFamily("Consolas,Courier New,monospace");
        f.setPointSize(8);
        pathLbl_->setFont(f);
    }
    pathLbl_->setStyleSheet("color: #3d3d3d;");
    pathLbl_->setAlignment(Qt::AlignHCenter);
    pathRowLayout->addWidget(pathLbl_);
    pathRow_->setVisible(printPath_);
    vbox->addWidget(pathRow_);

    // ── Key bindings ─────────────────────────────────────────────────────────
    fromUnitEdit_->installEventFilter(this);
    fromValueEdit_->installEventFilter(this);
    toUnitEdit_->installEventFilter(this);
    toValueEdit_->installEventFilter(this);
}

// ─────────────────────────────────────────────────────────────────────────────
void MainWindow::buildMenus()
{
    // ── File ──────────────────────────────────────────────────────────────────
    auto* fileMenu = menuBar()->addMenu("&File");
    fileMenu->addAction("Load memory…",  this, &MainWindow::onLoadMemory);
    fileMenu->addAction("Save memory…",  this, &MainWindow::onSaveMemory);
    fileMenu->addAction("Clean memory",  this, &MainWindow::onCleanMemory);
    fileMenu->addSeparator();
    fileMenu->addAction("E&xit", QKeySequence::Quit, qApp, &QApplication::quit);

    // ── Options ───────────────────────────────────────────────────────────────
    auto* optMenu = menuBar()->addMenu("&Options");
    optMenu->addAction("Set FVF…",       this, &MainWindow::onSetFvf);
    optMenu->addAction("Set timeout…",   this, &MainWindow::onSetTimeout);

    // Toggle path display
    auto* pathAct = optMenu->addAction("Show conversion path");
    pathAct->setCheckable(true);
    pathAct->setChecked(printPath_);
    connect(pathAct, &QAction::toggled, this, [this](bool checked) {
        printPath_ = checked;
        pathRow_->setVisible(checked);
        if (!checked) stopMarquee();
    });

    // ── Help ──────────────────────────────────────────────────────────────────
    auto* helpMenu = menuBar()->addMenu("&Help");
    helpMenu->addAction("Documentation",  this, &MainWindow::onDocumentation);
    helpMenu->addSeparator();
    helpMenu->addAction("About Unyts…",   this, &MainWindow::onAbout);
}

// ─────────────────────────────────────────────────────────────────────────────
bool MainWindow::eventFilter(QObject* obj, QEvent* event)
{
    if (event->type() == QEvent::KeyPress) {
        auto* ke = static_cast<QKeyEvent*>(event);
        if (ke->key() == Qt::Key_Return || ke->key() == Qt::Key_Enter) {
            // Enter in the to-value field → reverse conversion
            if (obj == toValueEdit_)
                onReverseConvert();
            else
                onConvert();
            return true;
        }
    }
    return QMainWindow::eventFilter(obj, event);
}

// ─────────────────────────────────────────────────────────────────────────────
// Parsing helpers
// ─────────────────────────────────────────────────────────────────────────────

std::optional<double> MainWindow::parseValue(const QString& s) const
{
    if (s.isEmpty()) return std::nullopt;
    bool ok = false;
    double v = s.toDouble(&ok);
    return ok ? std::optional<double>(v) : std::nullopt;
}

// ─────────────────────────────────────────────────────────────────────────────
void MainWindow::setStatus(const QString& msg, bool error)
{
    statusLbl_->setText(msg);
    statusLbl_->setStyleSheet(error ? "color: red;" : "color: #5f5f5f;");
}

// ─────────────────────────────────────────────────────────────────────────────
void MainWindow::doConvert(bool reverse)
{
    // Determine direction
    QString fromUnit  = (reverse ? toUnitEdit_  : fromUnitEdit_)->text().trimmed();
    QString fromValue = (reverse ? toValueEdit_ : fromValueEdit_)->text().trimmed();
    QString toUnit    = (reverse ? fromUnitEdit_  : toUnitEdit_)->text().trimmed();

    // Clear previous result
    (reverse ? fromValueEdit_ : toValueEdit_)->clear();
    stopMarquee();
    pathLbl_->clear();

    // Validate inputs
    if (fromUnit.isEmpty() || toUnit.isEmpty()) {
        setStatus("Enter source and target units.", true);
        return;
    }
    auto valOpt = parseValue(fromValue);
    if (!valOpt) {
        if (!fromValue.isEmpty())
            setStatus("Invalid number: " + fromValue, true);
        else
            setStatus("Enter a value to convert.", true);
        return;
    }

    // Apply search timeout for this call
    int prev = unyts::get_search_timeout_ms();
    unyts::set_search_timeout_ms(timeoutMs_);

    QElapsedTimer timer;
    timer.start();

    bool forceSearch = repeatSearch_->isChecked();
    if (forceSearch) {
        // BFS without cache — just run a fresh search (C++ engine always does
        // a live search; we don't currently persist search-path memory here)
    }

    auto result = unyts::convert(*valOpt,
                                 fromUnit.toStdString(),
                                 toUnit.toStdString());

    unyts::set_search_timeout_ms(prev);
    repeatSearch_->setChecked(false);

    qint64 elapsed = timer.elapsed();
    QString timeStr;
    if (elapsed < 1000)
        timeStr = QString::number(elapsed) + " ms";
    else
        timeStr = QString::number(elapsed / 1000.0, 'f', 2) + " s";

    if (!result) {
        setStatus("no conversion found!  (" + timeStr + ")", true);
        return;
    }

    // Display result
    double converted = result->value;
    QString resultStr;
    // Avoid unnecessary trailing zeros
    if (std::floor(converted) == converted && std::abs(converted) < 1e15)
        resultStr = QString::number(static_cast<long long>(converted));
    else
        resultStr = QString::number(converted, 'g', 10);

    (reverse ? fromValueEdit_ : toValueEdit_)->setText(resultStr);
    setStatus(timeStr);

    // Conversion path (the C++ engine doesn't yet expose path strings through
    // the public convert() API, so we synthesise a simple "A → B" label)
    if (printPath_) {
        QString pathStr = fromUnit + "  →  " + toUnit
                        + "  =  " + resultStr + "  " + toUnit;
        displayPath(pathStr);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
void MainWindow::onConvert()
{
    doConvert(false);
}

void MainWindow::onReverseConvert()
{
    doConvert(true);
}

// ─────────────────────────────────────────────────────────────────────────────
// Path marquee
// ─────────────────────────────────────────────────────────────────────────────

void MainWindow::displayPath(const QString& path)
{
    if (path.length() <= kMarqueeWidth) {
        stopMarquee();
        pathLbl_->setText(path);
    } else {
        startMarquee(path);
    }
}

void MainWindow::startMarquee(const QString& path)
{
    fullPathStr_ = path;
    marqueePos_  = 0;
    marqueeDir_  = true;
    pathLbl_->setText(path.left(kMarqueeWidth));
    marqueeTimer_.start(kMarqueeSpeed);
}

void MainWindow::stopMarquee()
{
    marqueeTimer_.stop();
    fullPathStr_.clear();
    marqueePos_ = 0;
}

void MainWindow::onMarqueeTick()
{
    int len = fullPathStr_.length();
    if (len <= kMarqueeWidth) { stopMarquee(); return; }

    pathLbl_->setText(fullPathStr_.mid(marqueePos_, kMarqueeWidth));

    if (marqueeDir_) {
        if (marqueePos_ + kMarqueeWidth < len) {
            ++marqueePos_;
        } else {
            marqueeDir_ = false;
            marqueeTimer_.start(kMarqueePause);
        }
    } else {
        if (marqueePos_ > 0) {
            --marqueePos_;
        } else {
            marqueeDir_ = true;
            marqueeTimer_.start(kMarqueePause);
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Menu handlers
// ─────────────────────────────────────────────────────────────────────────────

void MainWindow::onSetFvf()
{
    bool ok = false;
    double val = QInputDialog::getDouble(this,
        "Formation Volume Factor",
        "FVF value:",
        fvf_, 0.0001, 1e9, 6, &ok);
    if (ok) {
        fvf_ = val;
        setStatus(QString("FVF set to %1").arg(val));
    }
}

void MainWindow::onSetTimeout()
{
    bool ok = false;
    int val = QInputDialog::getInt(this,
        "Search Timeout",
        "Timeout (milliseconds):",
        timeoutMs_, 100, 60000, 500, &ok);
    if (ok) {
        timeoutMs_ = val;
        unyts::set_search_timeout_ms(val);
        setStatus(QString("Timeout set to %1 ms").arg(val));
    }
}

void MainWindow::onLoadMemory()
{
    // Search-path memory persistence is not yet implemented in the C++ engine;
    // show an informational message for now.
    QMessageBox::information(this, "Load Memory",
        "Memory persistence is not yet available in the C++ engine.");
}

void MainWindow::onSaveMemory()
{
    QMessageBox::information(this, "Save Memory",
        "Memory persistence is not yet available in the C++ engine.");
}

void MainWindow::onCleanMemory()
{
    QMessageBox::information(this, "Clean Memory",
        "Memory persistence is not yet available in the C++ engine.");
}

void MainWindow::onDocumentation()
{
    QDesktopServices::openUrl(QUrl("https://github.com/gg-dad/unyts"));
}

void MainWindow::onAbout()
{
    QMessageBox::about(this, "About Unyts",
        "<b>Unyts Converter</b> — C++ / Qt 6 edition<br>"
        "<br>"
        "A fast, graph-based unit conversion engine.<br>"
        "C++ core with pybind11 Python bindings.<br>"
        "<br>"
        "© Martín Carlos Araya");
}
