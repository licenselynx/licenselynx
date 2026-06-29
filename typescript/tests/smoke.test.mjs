/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import assert from 'node:assert/strict';
import test from 'node:test';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const distRoot = path.resolve(process.cwd(), 'dist');
const moduleUrl = pathToFileURL(path.join(distRoot, 'index.js')).href;
const { map, Organization } = await import(moduleUrl);

test('stable map lookup for 0BSD', async () => {
    const result = await map('0BSD');
    assert.ok(result);
    assert.equal(result.id, '0BSD');
});

test('risky map lookup with flag enabled for libpng-2.0', async () => {
    const result = await map('LIbpng License v2', true);
    assert.ok(result);
    assert.equal(result.id, 'libpng-2.0');
});

test('risky entry must not resolve without the flag', async () => {
    await assert.rejects(map('LIbpng License v2'));
});

test('organization-scoped lookup for SISL-1.5', async () => {
    const result = await map('Siemens Inner Source License v1.5', false, Organization.Siemens);
    assert.ok(result);
    assert.equal(result.id, 'SISL-1.5');
    assert.equal(result.src, 'siemens');
});

test('organization entry must not resolve without the org parameter', async () => {
    await assert.rejects(map('Siemens Inner Source License v1.5'));
});
