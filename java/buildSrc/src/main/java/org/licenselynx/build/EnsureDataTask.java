/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx.build;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Files;
import javax.annotation.Nonnull;
import javax.inject.Inject;

import org.gradle.api.DefaultTask;
import org.gradle.api.GradleException;
import org.gradle.api.Project;
import org.gradle.api.file.RegularFileProperty;
import org.gradle.api.provider.Property;
import org.gradle.api.tasks.CacheableTask;
import org.gradle.api.tasks.Input;
import org.gradle.api.tasks.OutputFile;
import org.gradle.api.tasks.TaskAction;


@CacheableTask
public class EnsureDataTask
    extends DefaultTask
{
    private final RegularFileProperty jsonFile;

    private final Property<String> jsonDownloadUrl;



    @Inject
    public EnsureDataTask(@Nonnull final Project pProject)
    {
        jsonFile = pProject.getObjects().fileProperty();
        jsonDownloadUrl = pProject.getObjects().property(String.class);
        setDescription("Ensures that the data file is present, downloading it if necessary.");
    }



    @TaskAction
    public void execute()
    {
        final File f = jsonFile.get().getAsFile();
        final String simpleName = f.getName();
        final File dataDir = f.getParentFile();

        if (!f.canRead()) {
            getLogger().lifecycle("{} not found. Downloading from {} ...", simpleName, jsonDownloadUrl.get());

            try (
                FileOutputStream fos = new FileOutputStream(f);
                BufferedOutputStream bos = new BufferedOutputStream(fos);
                InputStream inputStream = new URL(jsonDownloadUrl.get()).openStream())
            {
                byte[] buffer = new byte[16384];
                int bytesRead;
                Files.createDirectories(dataDir.toPath());
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    bos.write(buffer, 0, bytesRead);
                }
            }
            catch (IOException e) {
                throw new GradleException(getName() + " failed", e);
            }

            getLogger().lifecycle("Downloaded {} to {}", simpleName, jsonFile.get());
        }
        else {
            getLogger().info("{} exists, good.", simpleName);
        }
    }



    @Nonnull
    @OutputFile
    public RegularFileProperty getJsonFile()
    {
        return jsonFile;
    }



    @Input
    @Nonnull
    public Property<String> getJsonDownloadUrl()
    {
        return jsonDownloadUrl;
    }
}
