/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { pathToFileURL } from 'node:url';

const root = process.cwd();

test('packed package installs and exposes the library', async () => {
    const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'licenselynx-package-'));

    try {
        const filename = execFileSync('npm', ['pack', '--quiet', '--pack-destination', directory], {
            cwd: root,
            encoding: 'utf8',
        }).trim();
        const tarball = path.join(directory, filename);
        const packageJson = path.join(directory, 'package.json');

        assert.ok(await fs.stat(path.join(root, 'dist', 'index.js')));
        assert.ok(await fs.stat(path.join(root, 'dist', 'index.d.ts')));
        assert.ok(await fs.stat(path.join(root, 'dist', 'resources', 'merged_data.json')));
        await fs.writeFile(packageJson, JSON.stringify({ private: true }));
        execFileSync('npm', ['install', '--ignore-scripts', '--no-package-lock', tarball], {
            cwd: directory,
            stdio: 'inherit',
        });

        // Check if the license data is available
        const licenses = await import(pathToFileURL(path.join(root, 'dist', 'resources', 'merged_data.json')).href);
        assert.ok(licenses.stableMap);

        const modulePath = path.join(directory, 'node_modules', '@licenselynx', 'licenselynx', 'dist', 'index.js');
        const { map } = await import(pathToFileURL(modulePath).href);
        const result = await map('0BSD');

        assert.equal(result.id, '0BSD');
    } finally {
        await fs.rm(directory, { recursive: true, force: true });
    }
});
