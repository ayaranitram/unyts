import SwiftUI

/// A text field that shows a filtered dropdown of unit name suggestions.
struct UnitTextField: View {

    let label: String
    @Binding var text: String
    let allUnits: [String]

    @FocusState private var isFocused: Bool

    private var suggestions: [String] {
        guard !text.isEmpty else { return [] }
        return allUnits
            .filter { $0.localizedCaseInsensitiveContains(text) }
            .prefix(10)
            .map { $0 }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                TextField(label, text: $text)
                    .focused($isFocused)
                    .autocorrectionDisabled()
                    .textInputAutocapitalization(.never)

                if !text.isEmpty {
                    Button {
                        text = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(10)
            .background(Color(.systemGray6))
            .cornerRadius(8)

            if isFocused && !suggestions.isEmpty {
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 0) {
                        ForEach(suggestions, id: \.self) { unit in
                            Button {
                                text      = unit
                                isFocused = false
                            } label: {
                                Text(unit)
                                    .foregroundStyle(.primary)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 9)
                            }
                            .buttonStyle(.plain)
                            Divider()
                        }
                    }
                }
                .frame(maxHeight: 180)
                .background(Color(.systemBackground))
                .cornerRadius(8)
                .shadow(color: .black.opacity(0.12), radius: 6, y: 3)
                .zIndex(1)
            }
        }
    }
}
