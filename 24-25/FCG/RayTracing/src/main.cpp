#include <SFML/Graphics.hpp>
#include <vector>
#include <random>
#include <filesystem>
#include <chrono>
#include <iostream>

struct vec3 {
    float x, y, z;
    vec3(float x, float y, float z) : x(x), y(y), z(z) {}
    vec3(float v) : x(v), y(v), z(v) {}
};

struct Material {
    vec3 colour;
    vec3 emissionColour;
    float smoothness;
    float emissionStrength;
    float specularProbability;
    float ir;

    Material(const vec3& col, const vec3& emission = vec3(0,0,0), float emitStrength = 0.0f,float smooth = 0.0f,
             float specProb = 1.0f , float ir = 0.0f)
        : colour(col), emissionColour(emission),
          emissionStrength(emitStrength), smoothness(smooth), specularProbability(specProb) , ir(ir) {}
};

struct Sphere {
    vec3 center;
    float radius;
    Material material;
    
    Sphere(const vec3& c, float r, const Material& m) : center(c), radius(r), material(m) {}
};

int main() {
    // Configure anti-aliasing settings
    const unsigned int desiredAntiAliasing = 8;
    const unsigned int maxAntiAliasing = sf::RenderTexture::getMaximumAntiAliasingLevel();
    const unsigned int antiAliasingLevel = std::min(desiredAntiAliasing, maxAntiAliasing);
    
    sf::ContextSettings settings;
    settings.antiAliasingLevel = antiAliasingLevel;

    // Setup random number generation
    static std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<uint32_t> dist(0, UINT32_MAX);

    // Create main window with anti-aliasing
    sf::RenderWindow window(sf::VideoMode::getFullscreenModes().front(), 
                          "GLSL Shader Demo", sf::State::Fullscreen, settings);
    window.setFramerateLimit(60);
    window.setVerticalSyncEnabled(true);

    // Load shader
    sf::Shader shader;
    if (!shader.loadFromFile("../src/Raytracingshader.frag", sf::Shader::Type::Fragment)) {
        return -1;
    }

    // Create accumulation textures with anti-aliasing
    sf::RenderTexture accumTex0, accumTex1;
    const sf::Vector2u windowSize = window.getSize();
    
    if (!accumTex0.resize(windowSize, settings)) {
        return -1;
    }
    if (!accumTex1.resize(windowSize, settings)) {
        return -1;
    }
    
    accumTex0.clear(sf::Color::Black);
    accumTex1.clear(sf::Color::Black);
    accumTex0.display();
    accumTex1.display();

    // Create fullscreen quad
    sf::RectangleShape fullscreenQuad(sf::Vector2f(window.getSize()));

    // In main(), replace your spheres definition with:
    std::vector<Sphere> spheres;
    
    //---------------------add spheres here---------------------//

    // Add ground sphere (large sphere to act as ground)
    spheres.push_back({
        vec3(0.0f, -1000.0f, 0.0f), 1000.0f,
        Material(vec3(0.5f, 0.5f, 0.5f))
    });

    
    // Aggiungiamo una fila di sfere colorate
    // Sfera rossa
    spheres.push_back({
        vec3(-5.0f, 1.0f, 0.0f), 1.0f,
        Material(vec3(1.0f, 0.0f, 0.0f))
    });

    // Sfera gialla
    spheres.push_back({
        vec3(-2.5f, 1.0f, 0.0f), 1.0f,
        Material(vec3(0.5f, 0.5f, 0.0f))
    });

    // Sfera verde
    spheres.push_back({
        vec3(0.0f, 1.0f, 0.0f), 1.0f,
        Material(vec3(0.0f, 1.0f, 0.0f))
    });

    // Sfera ciano
    spheres.push_back({
        vec3(2.5f, 1.0f, 0.0f), 1.0f,
        Material(vec3(0.0f, 0.5f, 0.5f))
    });

    // Sfera blu
    spheres.push_back({
        vec3(5.0f, 1.0f, 0.0f), 1.0f,
        Material(vec3(0.0f, 0.0f, 1.0f))
    });

    //--------------------------------------------------------------//

    std::vector<sf::Glsl::Vec3> sphereCenters;
    std::vector<float> sphereRadii;
    std::vector<sf::Glsl::Vec3> sphereColors, sphereEmissionColors;
    std::vector<float> sphereEmissionStrengths, sphereSmoothness, sphereSpecularProbs, sphereIRs;

    for (const auto& sphere : spheres) {
        sphereCenters.emplace_back(sphere.center.x, sphere.center.y, sphere.center.z);
        sphereRadii.push_back(sphere.radius);
        sphereColors.emplace_back(sphere.material.colour.x, sphere.material.colour.y, sphere.material.colour.z);
        sphereEmissionColors.emplace_back(sphere.material.emissionColour.x, 
                                        sphere.material.emissionColour.y, 
                                        sphere.material.emissionColour.z);
        sphereSmoothness.push_back(sphere.material.smoothness);
        sphereEmissionStrengths.push_back(sphere.material.emissionStrength);
        sphereSpecularProbs.push_back(sphere.material.specularProbability);
        sphereIRs.push_back(sphere.material.ir);
    }

    shader.setUniformArray("sphereCenters", sphereCenters.data(), sphereCenters.size());
    shader.setUniformArray("sphereRadii", sphereRadii.data(), sphereRadii.size());
    shader.setUniformArray("sphereColors", sphereColors.data(), sphereColors.size());
    shader.setUniformArray("sphereEmissionColors", sphereEmissionColors.data(), sphereEmissionColors.size());
    shader.setUniformArray("sphereEmissionStrengths", sphereEmissionStrengths.data(), sphereEmissionStrengths.size());
    shader.setUniformArray("sphereSmoothness", sphereSmoothness.data(), sphereSmoothness.size());
    shader.setUniformArray("sphereSpecularProbs", sphereSpecularProbs.data(), sphereSpecularProbs.size());
    shader.setUniformArray("sphereIRs", sphereIRs.data(), sphereIRs.size());


    shader.setUniform("resolution", sf::Vector2f(window.getSize()));
    shader.setUniform("numSpheres", static_cast<int>(spheres.size()));

    sf::Clock clock;
    bool useFirstTexture = true;
    int frameCount = 0;

    while (window.isOpen()) {
        frameCount++;

        window.handleEvents(
            [&](const sf::Event::Closed&) { window.close(); },
            [&](const sf::Event::KeyPressed& keyPressed) {
                if (keyPressed.scancode == sf::Keyboard::Scancode::Escape)
                    window.close();
                if (keyPressed.scancode == sf::Keyboard::Scancode::Space) {
                    frameCount = 0;
                    accumTex0.clear(sf::Color::Black);
                    accumTex0.display();
                    accumTex1.clear(sf::Color::Black);
                    accumTex1.display();
                }
                if (keyPressed.scancode == sf::Keyboard::Scancode::S) {
                    // Create screenshots directory if it doesn't exist
                    std::filesystem::path screenshotsDir = "../renders";
                    if (!std::filesystem::exists(screenshotsDir)) {
                        std::filesystem::create_directory(screenshotsDir);
                    }
                    
                    // Get current texture
                    const auto& texToSave = useFirstTexture ? accumTex0 : accumTex1;
                    
                    // Generate filename with timestamp
                    auto now = std::chrono::system_clock::now();
                    auto timestamp = std::chrono::duration_cast<std::chrono::seconds>(
                        now.time_since_epoch()).count();
                    std::string filename = "../renders/render" + 
                                          std::to_string(timestamp) + ".png";
                    
                    // Save screenshot
                    if (!texToSave.getTexture().copyToImage().saveToFile(filename)) {
                        std::cerr << "Failed to save screenshot to: " << filename << std::endl;
                    }
                    std::cout << "Screenshot saved to: " << filename << std::endl;
                }
            }
        );


        shader.setUniform("time", clock.getElapsedTime().asSeconds());
        shader.setUniform("frameCount", static_cast<int>(frameCount - 1));
        shader.setUniform("randomSeed", static_cast<int>(dist(rng)));


        auto& prevTex = useFirstTexture ? accumTex0 : accumTex1;
        auto& currTex = useFirstTexture ? accumTex1 : accumTex0;
        
        shader.setUniform("accumulatedTex", prevTex.getTexture());
        currTex.clear();
        currTex.draw(fullscreenQuad, &shader);
        currTex.display();

        window.clear();
        sf::Sprite finalSprite(currTex.getTexture());
        window.draw(finalSprite);
        window.display();

        useFirstTexture = !useFirstTexture;
    }

    return 0;
}