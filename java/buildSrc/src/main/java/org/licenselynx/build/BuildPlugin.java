/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx.build;

import javax.annotation.Nonnull;

import org.gradle.api.Plugin;
import org.gradle.api.Project;
import org.gradle.api.file.FileCollection;
import org.gradle.api.tasks.SourceSet;
import org.gradle.api.tasks.SourceSetContainer;
import org.gradle.api.tasks.TaskProvider;


public class BuildPlugin
    implements Plugin<Project>
{
    @Override
    public void apply(@Nonnull final Project pRootProject)
    {
        final Project project = pRootProject.getRootProject();

        final TaskProvider<EnsureDataTask> ensureDataTaskProvider = project.getTasks().register("checkAndDownloadJson",
            EnsureDataTask.class);
        ensureDataTaskProvider.configure(t -> {
            t.getJsonDownloadUrl().set("https://licenselynx.org/json/latest/mapping.json");
            t.getJsonFile().set(project.getLayout().getBuildDirectory().dir("licenselynx/data").get()
                .file("merged_data.json").getAsFile());
        });

        final TaskProvider<CodeGeneratorTask> generateCodeTaskProvider = project.getTasks().register("generateJava",
            CodeGeneratorTask.class);
        generateCodeTaskProvider.configure(t -> {
            t.getJsonFile().set(ensureDataTaskProvider.flatMap(EnsureDataTask::getJsonFile));
            t.getTemplateFiles().setFrom(getTemplateFiles(project));
            t.getGeneratedJavaDir().set(project.getLayout().getBuildDirectory().dir("licenselynx/java"));
        });
    }



    private FileCollection getTemplateFiles(@Nonnull final Project pProject)
    {
        SourceSetContainer sourceSets = pProject.getExtensions().getByType(SourceSetContainer.class);
        SourceSet templatesSourceSet = sourceSets.getByName("templates");
        return templatesSourceSet.getJava();
    }
}
