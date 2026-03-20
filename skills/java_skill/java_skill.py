from agent_framework import Skill
from textwrap import dedent                                                                     

def java_skill():
    return Skill(
        name="java-generator",
        description="Generate Spring Boot Java/XML files",
        content=dedent("""
YOU GENERATE COMPLETE FILES (JAVA OR XML).

========================================================
RULES — MUST FOLLOW
========================================================
No markdown
No explanations
No comments outside code
No natural language
Only RAW, valid Java or XML code
Generates the business logic in Java necessary for the proper functioning of the microservice
Use ONLY spring-boot-starter-web
always generates controllers, services and models that work together to fulfill the requirements. No placeholders.
create the necessary logic to call external API in the requirements, using WebClient.
========================================================

INPUT JSON:
{
  "requirements": {...},
  "file": {"path": "...", "type": "..."},
  "package": "com.example.xxx"
}

========================================================
FILE TYPES
========================================================

1) type = "pom"
Produce a complete Spring Boot pom.xml:
- parent: spring-boot-starter-parent
- java.version: 17
- dependencies:
    spring-boot-starter-web
    spring-boot-starter-validation
    lombok
    spring-boot-starter-test
- build: spring-boot-maven-plugin
NO COMMENTS.


2) type = "main"
Example:
package <package>.application;

import org.springframework.boot.*;
import org.springframework.boot.autoconfigure.*;

@SpringBootApplication
public class Application {
  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }
}


3) type = "controller"
- @RestController
- @RequestMapping("/api")
- For each endpoint:
    - generate method
    - call service layer
    - return model


4) type = "service"
- @Service
- If external APIs exist:
    - Use WebClient
    - Call external API
    - Map JSON → model class
    - Return mapped model


5) type = "model"
- Plain POJO
- fields from requirements.models
- generate getters and setters
- generate constructors
========================================================

OUTPUT:
ONLY the code. NOTHING ELSE.
""")
    )