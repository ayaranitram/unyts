import Foundation

/// A single completed conversion, kept in the history list.
struct ConversionRecord: Identifiable, Codable {
    let id:        UUID
    let fromValue: Double
    let fromUnit:  String
    let toValue:   Double
    let toUnit:    String
    let date:      Date
}
