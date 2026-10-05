import re

with open('android/build.gradle.kts', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import at the top
if "import org.jetbrains.kotlin.gradle.tasks.KotlinCompile" not in content:
    content = "import org.jetbrains.kotlin.gradle.tasks.KotlinCompile\n" + content

# Replace the subprojects evaluation block
old_block = """subprojects {
    project.evaluationDependsOn(":app")
}"""

new_block = """subprojects {
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

content = content.replace(old_block, new_block)

with open('android/build.gradle.kts', 'w', encoding='utf-8') as f:
    f.write(content)
