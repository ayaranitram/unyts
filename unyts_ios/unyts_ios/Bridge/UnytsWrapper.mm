// UnytsWrapper.mm — Objective-C++ implementation of the unyts bridge.
//
// The .mm extension tells the compiler to process this file as
// Objective-C++ so that C++ headers can be included alongside ObjC code.

#import "UnytsWrapper.h"
#include "unyts/unyts_capi.h"
#include <cstdlib>

static NSString * const kUnytsErrorDomain = @"com.unyts";

@implementation UnytsWrapper {
    UnytsContext *_ctx;
}

- (instancetype)init {
    self = [super init];
    if (self) {
        _ctx = unyts_create();
    }
    return self;
}

- (void)dealloc {
    unyts_destroy(_ctx);
    _ctx = NULL;
}

// ── Conversion ────────────────────────────────────────────────────────────────

- (BOOL)convertValue:(double)value
            fromUnit:(NSString *)fromUnit
              toUnit:(NSString *)toUnit
            outValue:(double *)outValue
               error:(NSError **)error
{
    double result = 0.0;
    int rc = unyts_convert(_ctx, value, fromUnit.UTF8String, toUnit.UTF8String, &result);

    if (rc == UNYTS_OK) {
        if (outValue) *outValue = result;
        return YES;
    }

    if (error) {
        NSString *msg = [NSString stringWithFormat:@"No conversion path: %@ → %@",
                         fromUnit, toUnit];
        *error = [NSError errorWithDomain:kUnytsErrorDomain
                                     code:rc
                                 userInfo:@{NSLocalizedDescriptionKey: msg}];
    }
    return NO;
}

- (BOOL)isConvertibleFrom:(NSString *)fromUnit to:(NSString *)toUnit {
    return unyts_convertible(_ctx, fromUnit.UTF8String, toUnit.UTF8String) == 1;
}

// ── Unit discovery ────────────────────────────────────────────────────────────

- (NSArray<NSString *> *)allUnits {
    const int kBufSize = 1 << 20; // 1 MB — sufficient for ~1700 unit names
    char *buf = static_cast<char *>(malloc(kBufSize));
    if (!buf) return @[];

    unyts_all_units(_ctx, buf, kBufSize);
    NSString *raw = [NSString stringWithUTF8String:buf];
    free(buf);

    if (!raw) return @[];

    NSArray<NSString *> *parts = [raw componentsSeparatedByString:@"\n"];
    NSPredicate *nonEmpty = [NSPredicate predicateWithFormat:@"length > 0"];
    NSArray<NSString *> *filtered = [parts filteredArrayUsingPredicate:nonEmpty];
    return [filtered sortedArrayUsingSelector:@selector(localizedCaseInsensitiveCompare:)];
}

- (BOOL)isKnownUnit:(NSString *)unitName {
    return unyts_is_known_unit(_ctx, unitName.UTF8String) == 1;
}

// ── Settings ──────────────────────────────────────────────────────────────────

- (double)fvf {
    return unyts_get_fvf(_ctx);
}
- (void)setFvf:(double)fvf {
    unyts_set_fvf(_ctx, fvf);
}

- (NSInteger)timeoutMs {
    return (NSInteger)unyts_get_timeout_ms(_ctx);
}
- (void)setTimeoutMs:(NSInteger)timeoutMs {
    unyts_set_timeout_ms(_ctx, (int)timeoutMs);
}

- (NSString *)version {
    return [NSString stringWithUTF8String:unyts_version()];
}

@end
