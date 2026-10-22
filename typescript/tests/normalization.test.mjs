/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
import test from "node:test";
import { map } from "../dist/index.js";

const spec = JSON.parse(fs.readFileSync(new URL("../../fixtures/normalization.json", import.meta.url), "utf8"));

const { stableMap } = createRequire(import.meta.url)("../dist/resources/merged_data.json");

const assertNormalizes = (input, expected) => {
    const sentinel = { id: "normalization-sentinel", src: "custom" };
    const previous = Object.getOwnPropertyDescriptor(stableMap, expected);
    stableMap[expected] = sentinel;
    try {
        assert.equal(map(input).id, sentinel.id);
    } finally {
        if (previous) {
            Object.defineProperty(stableMap, expected, previous);
        } else {
            delete stableMap[expected];
        }
    }
};

const codePoint = (char) => `U+${char.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`;

for (const { name, input, expected } of spec.testCases) {
    test(`normalization case: ${name}`, () => assertNormalizes(input, expected));
}

for (const quote of spec.quoteCharacters) {
    test(`replaces quote ${codePoint(quote)}`, () => assertNormalizes(`a${quote}b`, `a${spec.quoteReplacement}b`));
}

for (const char of spec.trimCharacters) {
    test(`trims ${codePoint(char)}`, () => assertNormalizes(`${char}a${char}`, "a"));
}
