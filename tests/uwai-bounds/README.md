# UWAI missing-ID accessor fixture

The three accessors in check.cpp are extracted from the corrected production methods. Globals, assertions, enum metadata and scaled are reduced stand-ins. Assertions record the invalid range and allow execution to continue, modeling release continuation. The fixture checks 252 combinations across zero/1/2/29/64 metadata entries, valid IDs, negative IDs, upper bounds, INT_MIN/INT_MAX, NULL or populated leader arrays, and positive/zero/negative valid weights. Valid names retain pointer identity. Invalid IDs cause no global metadata lookup and return zero weight / a non-NULL empty wide string.

Run from the repository root:

```sh
g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fno-exceptions tests/uwai-bounds/check.cpp -o /tmp/uwai-bounds
/tmp/uwai-bounds
g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fno-exceptions -fsanitize=address,undefined -fno-omit-frame-pointer tests/uwai-bounds/check.cpp -o /tmp/uwai-bounds-san
ASAN_OPTIONS=detect_leaks=0 /tmp/uwai-bounds-san
```

Original-method negative controls aborted on both attempted global -1 lookups; ASan reproduced a heap-buffer-overflow in the original populated leader-array accessor. This does not execute Civ4's XML loader, actual fixed-point implementation, debug dialogs or gameplay. Leak detection was disabled; no leak claim. The supplied aspect XML already has all 29 required keys; this correction handles an incomplete/failed metadata load, not a claim that current assets omit a key.
