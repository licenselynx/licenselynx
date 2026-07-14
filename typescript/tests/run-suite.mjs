/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import { spawnSync } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';

const mode = process.argv[2];
if (mode !== 'unit' && mode !== 'smoke' && mode !== 'package') {
    throw new Error(`Unsupported test mode: ${mode}`);
}

const root = process.cwd();
const resourcesPath = path.join(root, 'resources', 'merged_data.json');
const unitFixturePath = path.join(root, 'tests', 'resources', 'merged_data.json');
const originalResources = await fs.readFile(resourcesPath, 'utf8');

const run = (command, args) => {
    const result = spawnSync(command, args, {
        cwd: root,
        stdio: 'inherit',
    });

    if (result.status !== 0) {
        process.exit(result.status ?? 1);
    }
};

try {
    if (mode === 'unit') {
        await fs.writeFile(resourcesPath, await fs.readFile(unitFixturePath, 'utf8'));
        run('npm', ['run', 'build']);
        await fs.rm(path.join(root, 'coverage'), { recursive: true, force: true });
        run('npx', ['c8', '--reporter=text', '--reporter=lcov', '--report-dir', 'coverage', 'tsx', '--test', 'tests/unit.test.mjs']);
    } else {
        run('python3', ['../scripts/src/load/merge_data.py', '-o', './resources/merged_data.json']);
        run('npm', ['run', 'build']);
        run('npx', ['tsx', '--test', `tests/${mode}.test.mjs`]);
    }
} finally {
    await fs.writeFile(resourcesPath, originalResources);
}
