#include <SFML/Graphics.hpp>
#include <vector>
#include <random>

struct vec3 {
    float x, y, z;
    vec3(float x, float y, float z) : x(x), y(y), z(z) {}
};

struct Material {
    vec3 colour;
    vec3 emissionColour;
    vec3 specularColour;
    float emissionStrength;
    float smoothness;
    float specularProbability;
    float ir;

    Material(const vec3& col, const vec3& emission = vec3(0,0,0), 
            const vec3& specular = vec3(1,1,1), float emitStrength = 0.0f,
            float smooth = 0.0f, float specProb = 0.0f , float ir = 0.0f)
        : colour(col), emissionColour(emission), specularColour(specular),
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
    window.setFramerateLimit(30);

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
    
    // Add ground sphere (large sphere to act as ground)
    spheres.push_back({
        vec3(0.0f, -1000.0f, 0.0f), 1000.0f,
        Material(vec3(0.5f, 0.5f, 0.5f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
    });
    
    // Add the three large special spheres
    // Lambertian sphere
    spheres.push_back({
        vec3(-4.0f, 1.0f, 0.0f), 1.0f,
        Material(vec3(0.4f, 0.2f, 0.1f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
    });

    spheres.push_back({
        vec3(-4.0f, 1.0f, -3.0f), .3f,
        Material(vec3(0.4f, 0.2f, 0.1f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
    });

    // Glass sphere
    spheres.push_back({
        vec3(0.0f, 1.0f, 0.0f), 1.0f,
        Material(vec3(1.0f, 1.0f, 1.0f), vec3(0, 0, 0), vec3(1, 1, 1), 0.0f, 1.0f, 0.0f, 1.5f)
    });

    spheres.push_back({
        vec3(0.0f, 1.0f, 0.0f), .5f,
        Material(vec3(1.0f, 0.0f, 0.0f), vec3(0, 0, 0), vec3(1, 1, 1), 0.0f, 1.0f, 0.0f, 1.f)
    });


    spheres.push_back({
        vec3(0.0f, 1.0f, 0.0f), .7f,
        Material(vec3(1.0f, 1.0f, 1.0f), vec3(0, 0, 0), vec3(1, 1, 1), 0.0f, 1.0f, 0.0f, 1.f)
    });
    
    // Metal sphere
    spheres.push_back({
        vec3(4.0f, 1.0f, -1.0f), 1.0f,
        Material(vec3(0.7f, 0.6f, 0.5f), vec3(0, 0, 0), vec3(1, 1, 1), 0.0f, 1.0f, 1.0f, 0.0f)
    });

    //light source
    spheres.push_back({
        vec3(0.0f, 2.0f, 4.0f), 2.0f,
        Material(vec3(0.7f, 0.6f, 0.5f), vec3(1, .8, 0.0), vec3(1, 1, 1), 3.0f, 0.0f, 1.0f, 0.0f)
    });

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
            }
        );


        shader.setUniform("time", clock.getElapsedTime().asSeconds());
        shader.setUniform("resolution", sf::Vector2f(window.getSize()));
        shader.setUniform("numSpheres", static_cast<int>(spheres.size()));
        shader.setUniform("frameCount", static_cast<int>(frameCount - 1));
        shader.setUniform("randomSeed", static_cast<int>(dist(rng)));

        std::vector<sf::Glsl::Vec3> sphereCenters;
        std::vector<float> sphereRadii;
        std::vector<sf::Glsl::Vec3> sphereColors, sphereEmissionColors, sphereSpecularColors;
        std::vector<float> sphereEmissionStrengths, sphereSmoothness, sphereSpecularProbs, sphereIRs;

        for (const auto& sphere : spheres) {
            sphereCenters.emplace_back(sphere.center.x, sphere.center.y, sphere.center.z);
            sphereRadii.push_back(sphere.radius);
            sphereColors.emplace_back(sphere.material.colour.x, sphere.material.colour.y, sphere.material.colour.z);
            sphereEmissionColors.emplace_back(sphere.material.emissionColour.x, 
                                            sphere.material.emissionColour.y, 
                                            sphere.material.emissionColour.z);
            sphereSpecularColors.emplace_back(sphere.material.specularColour.x, 
                                            sphere.material.specularColour.y, 
                                            sphere.material.specularColour.z);
            sphereEmissionStrengths.push_back(sphere.material.emissionStrength);
            sphereSmoothness.push_back(sphere.material.smoothness);
            sphereSpecularProbs.push_back(sphere.material.specularProbability);
            sphereIRs.push_back(sphere.material.ir);
        }

        shader.setUniformArray("sphereCenters", sphereCenters.data(), sphereCenters.size());
        shader.setUniformArray("sphereRadii", sphereRadii.data(), sphereRadii.size());
        shader.setUniformArray("sphereColors", sphereColors.data(), sphereColors.size());
        shader.setUniformArray("sphereEmissionColors", sphereEmissionColors.data(), sphereEmissionColors.size());
        shader.setUniformArray("sphereSpecularColors", sphereSpecularColors.data(), sphereSpecularColors.size());
        shader.setUniformArray("sphereEmissionStrengths", sphereEmissionStrengths.data(), sphereEmissionStrengths.size());
        shader.setUniformArray("sphereSmoothness", sphereSmoothness.data(), sphereSmoothness.size());
        shader.setUniformArray("sphereSpecularProbs", sphereSpecularProbs.data(), sphereSpecularProbs.size());
        shader.setUniformArray("sphereIRs", sphereIRs.data(), sphereIRs.size());

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