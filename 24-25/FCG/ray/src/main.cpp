// main.cpp
#include <SFML/Graphics.hpp>
#include <vector>
#include <sstream>
#include <fstream>
#include <cstdint>

struct Material {
    sf::Color albedo;
    float metallic;
    float roughness;
};

struct Model {
    std::vector<sf::Vector3f> vertices;
    std::vector<sf::Vector3f> normals;
    sf::Vector3f position;
    Material material;
};

Model loadOBJ(const std::string& filename) {
    Model model;
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        throw sf::Exception("Failed to open OBJ file: " + filename);
    }

    std::vector<sf::Vector3f> temp_positions;
    std::vector<sf::Vector3f> temp_normals;
    std::string line;

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string prefix;
        iss >> prefix;

        if (prefix == "v") {
            // Vertex position
            float x, y, z;
            iss >> x >> y >> z;
            temp_positions.emplace_back(x, y, z);
        }
        else if (prefix == "vn") {
            // Vertex normal
            float nx, ny, nz;
            iss >> nx >> ny >> nz;
            temp_normals.emplace_back(nx, ny, nz);
        }
        else if (prefix == "f") {
            // Face definition (triangulated)
            std::vector<std::string> faceVertices;
            std::string vertex;
            while (iss >> vertex) {
                faceVertices.push_back(vertex);
            }

            // Triangulate face (supports both triangles and quads)
            for (size_t i = 1; i < faceVertices.size() - 1; ++i) {
                // Process each triangle in the polygon
                for (const auto& index : {faceVertices[0], faceVertices[i], faceVertices[i+1]}) {
                    std::istringstream viss(index);
                    std::string part;
                    std::vector<std::string> parts;
                    
                    while (std::getline(viss, part, '/')) {
                        parts.push_back(part);
                    }

                    // Get position index (OBJ uses 1-based indexing)
                    int posIndex = -1;
                    if (!parts[0].empty()) {
                        posIndex = std::stoi(parts[0]) - 1;
                    }

                    // Get normal index (if present)
                    int normIndex = -1;
                    if (parts.size() >= 3 && !parts[2].empty()) {
                        normIndex = std::stoi(parts[2]) - 1;
                    }

                    // Validate and store indices
                    if (posIndex >= 0 && posIndex < temp_positions.size()) {
                        model.vertices.push_back(temp_positions[posIndex]);
                        
                        if (normIndex >= 0 && normIndex < temp_normals.size()) {
                            model.normals.push_back(temp_normals[normIndex]);
                        }
                        else {
                            // If no normal, push default
                            model.normals.push_back(sf::Vector3f(0, 0, 0));
                        }
                    }
                }
            }
        }
    }

    if (model.vertices.empty()) {
        throw sf::Exception("No valid geometry found in OBJ file");
    }

    // Set default material properties
    model.material = {
        sf::Color::White,  // Albedo
        0.5f,              // Metallic
        0.5f               // Roughness
    };

    return model;
}


int main() {
    // Create window with SFML 3.0 syntax
    sf::RenderWindow window(
        sf::VideoMode::getFullscreenModes().front(),
        "SFML 3 Ray Tracer",
        sf::State::Fullscreen
    );
    window.setFramerateLimit(60);

    // Load models
    std::vector<Model> models;
    try {
        models.push_back(loadOBJ("../src/piece.obj"));
    } catch (const sf::Exception& e) {
        return -1;
    }

    // Load ray tracing shader
    sf::Shader raytracer;
    if (!raytracer.loadFromFile("../src/raytracer.frag", sf::Shader::Type::Fragment)) {
        return -1;
    }

    // Create fullscreen quad
    sf::RectangleShape fullscreenQuad(sf::Vector2f(window.getSize()));
    sf::Clock clock;

    // Main loop
    while (window.isOpen()) {
        // Event handling with SFML 3.0 syntax
        window.handleEvents(
            [&](const sf::Event::Closed&) { window.close(); },
            [&](const sf::Event::KeyPressed& key) {
                if (key.scancode == sf::Keyboard::Scancode::Escape)
                    window.close();
            },
            [](const auto&) {}
        );

        // Update shader uniforms
        raytracer.setUniform("time", clock.getElapsedTime().asSeconds());
        raytracer.setUniform("resolution", sf::Vector2f(window.getSize()));
        
        // Pass model data to shader
        std::vector<sf::Glsl::Vec4> modelData;
        for (const auto& model : models) {
            modelData.emplace_back(model.position.x, model.position.y, model.position.z, 0);
            modelData.emplace_back(
                model.material.albedo.r / 255.f,
                model.material.albedo.g / 255.f,
                model.material.albedo.b / 255.f,
                model.material.metallic
            );
            modelData.emplace_back(model.material.roughness, 0, 0, 0);
        }
        raytracer.setUniformArray("models", modelData.data(), modelData.size());
        raytracer.setUniform("numModels", static_cast<int>(models.size()));

        // Draw scene
        window.clear(sf::Color::Black);
        window.draw(fullscreenQuad, &raytracer);
        window.display();
    }

    return 0;
}