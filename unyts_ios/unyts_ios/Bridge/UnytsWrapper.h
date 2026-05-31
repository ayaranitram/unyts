#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

/**
 * Wraps the unyts pure-C API behind an Objective-C++ interface that Swift can
 * call directly via the bridging header.
 *
 * One instance should be created at app launch and kept alive for the
 * application's lifetime (the underlying UnytsContext is inexpensive to hold,
 * and graph initialisation is cached globally within the process).
 */
@interface UnytsWrapper : NSObject

/** Create and initialise a unyts context.  Expensive on first call (graph build). */
- (instancetype)init NS_DESIGNATED_INITIALIZER;

/**
 * Convert [value] from [fromUnit] to [toUnit].
 *
 * @param outValue  Receives the result on success; unchanged on failure.
 * @param error     Populated with an NSError on failure; may be nil.
 * @return          YES on success, NO if no conversion path exists.
 */
- (BOOL)convertValue:(double)value
            fromUnit:(NSString *)fromUnit
              toUnit:(NSString *)toUnit
            outValue:(double *)outValue
               error:(NSError *_Nullable *)error;

/** Returns YES if a conversion path exists between [fromUnit] and [toUnit]. */
- (BOOL)isConvertibleFrom:(NSString *)fromUnit to:(NSString *)toUnit;

/** Sorted array of all known unit names. */
- (NSArray<NSString *> *)allUnits;

/** Returns YES if [unitName] is a known unit name or alias. */
- (BOOL)isKnownUnit:(NSString *)unitName;

/** Formation Volume Factor (default 1.0). */
@property(nonatomic) double fvf;

/** Search timeout in milliseconds (default 5000). */
@property(nonatomic) NSInteger timeoutMs;

/** Library version string, e.g. "0.1.0". */
@property(nonatomic, readonly) NSString *version;

@end

NS_ASSUME_NONNULL_END
