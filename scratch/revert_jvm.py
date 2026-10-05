import re

with open('android/build.gradle.kts', 'r', encoding='utf-8') as f:
    content = f.read()

# Revert the JVM forcing block completely
old_block = """subprojects {
    project.evaluationDependsOn(":app")
    
    tasks.withType<JavaCompile>().configureEach {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }
    tasks.withType<KotlinCompile>().configureEach {
        kotlinOptions {
            jvmTarget = "17"
        }
    }
}"""

new_block = """subprojects {
    project.evaluationDependsOn(":app")
}"""

content = content.replace(old_block, new_block)
content = content.replace("import org.jetbrains.kotlin.gradle.tasks.KotlinCompile\n", "")

with open('android/build.gradle.kts', 'w', encoding='utf-8') as f:
    f.write(content)
