/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import assert from 'node:assert/strict';
import test from 'node:test';
import { map, Organization } from '../dist/index.js';

test('stable map lookup for 0BSD', () => {
    const result = map('0BSD');
    assert.ok(result);
    assert.equal(result.id, '0BSD');
});

test('risky map lookup with flag enabled for libpng-2.0', () => {
    const result = map('LIbpng License v2', true);
    assert.ok(result);
    assert.equal(result.id, 'libpng-2.0');
});

test('risky entry must not resolve without the flag', () => {
    assert.throws(() => map('LIbpng License v2'));
});

test('organization-scoped lookup for SISL-1.5', () => {
    const result = map('Siemens Inner Source License v1.5', false, Organization.Siemens);
    assert.ok(result);
    assert.equal(result.id, 'SISL-1.5');
    assert.equal(result.src, 'siemens');
});

test('organization entry must not resolve without the org parameter', () => {
    assert.throws(() => map('Siemens Inner Source License v1.5'));
});
