#include <SFML/Graphics.hpp>
#include <SFML/System/Vector3.hpp>
#include <vector>

struct vec3 {
    float x, y, z;
    
    vec3(float x, float y, float z) : x(x), y(y), z(z) {}
};

// Material properties matching the shader's RayTracingMaterial
struct Material {
    vec3 colour;
    vec3 emissionColour;
    vec3 specularColour;
    float emissionStrength;
    float smoothness;
    float specularProbability;
    
    Material(const vec3& col, const vec3& emission = vec3(0,0,0), const vec3& specular = vec3(1,1,1), 
             float emitStrength = 0.0f, float smooth = 0.0f, float specProb = 0.0f)
        : colour(col), emissionColour(emission), specularColour(specular),
          emissionStrength(emitStrength), smoothness(smooth), specularProbability(specProb) {}
};

struct Sphere {
    vec3 center;
    float radius;
    Material material;
    
    Sphere(const vec3& c, float r, const Material& m) : center(c), radius(r), material(m) {}
};

int main()
{
    // Create window with SFML 3.0 syntax
    //sf::RenderWindow window(sf::VideoMode({800, 600}), "GLSL Shader Demo", sf::State::Windowed);
    sf::RenderWindow window(sf::VideoMode::getFullscreenModes().front(), "GLSL Shader Demo", sf::State::Fullscreen);
    window.setFramerateLimit(60);

    // Load fragment shader
    sf::Shader shader;
    if (!shader.loadFromFile("../src/Raytracingshader.frag", sf::Shader::Type::Fragment))
    {
        return -1;
    }

    // Create fullscreen rectangle
    sf::RectangleShape fullscreenQuad(sf::Vector2f(window.getSize()));

    // Create multiple spheres with materials
    std::vector<Sphere> spheres;
    
    // Red sphere with some emission
    Material redMaterial(vec3(1.0f, 0.2f, 0.2f), vec3(1.0f, 0.1f, 0.1f), vec3(1.0f, 1.0f, 1.0f), 0.2f, 0.7f, 0.1f);
    spheres.push_back(Sphere(vec3(0.0f, 0.0f, -3.0f), 1.0f, redMaterial));
    
    // Blue sphere with high smoothness (more reflective)
    Material blueMaterial(vec3(0.2f, 0.4f, 1.0f), vec3(0.0f, 0.0f, 0.0f), vec3(1.0f, 1.0f, 1.0f), 0.0f, 0.9f, 0.8f);
    spheres.push_back(Sphere(vec3(2.0f, 0.0f, -3.0f), .7f, blueMaterial));
    
    // Green sphere with some emission
    Material greenMaterial(vec3(0.2f, 0.8f, 0.2f), vec3(0.1f, 0.6f, 0.1f), vec3(0.8f, 1.0f, 0.8f), 0.4f, 0.3f, 0.2f);
    spheres.push_back(Sphere(vec3(-0.0f, -101.0f, -3.0f), 100.0f, greenMaterial));

    // Define maximum number of spheres (must match shader)
    const int MAX_SPHERES = 30;

    sf::Clock clock;

    // Main loop with SFML 3.0 event handling
    while (window.isOpen())
    {
        window.handleEvents(
            [&](const sf::Event::Closed&) { window.close(); },
            [&](const sf::Event::KeyPressed& keyEvent) {
                if (keyEvent.scancode == sf::Keyboard::Scancode::Escape)
                    window.close();
            },
            [](const auto&) {}  // Catch-all
        );
        
        // Update shader uniforms
        shader.setUniform("time", clock.getElapsedTime().asSeconds());
        shader.setUniform("resolution", sf::Vector2f(window.getSize()));
        
        // Pass sphere count to shader
        shader.setUniform("numSpheres", static_cast<int>(spheres.size()));
        
        // Prepare arrays for sphere data
        std::vector<sf::Glsl::Vec3> sphereCenters;
        std::vector<float> sphereRadii;
        std::vector<sf::Glsl::Vec3> sphereColors;
        std::vector<sf::Glsl::Vec3> sphereEmissionColors;
        std::vector<sf::Glsl::Vec3> sphereSpecularColors;
        std::vector<float> sphereEmissionStrengths;
        std::vector<float> sphereSmoothness;
        std::vector<float> sphereSpecularProbs;
        
        // Fill arrays with sphere data
        for (const auto& sphere : spheres) {
            sphereCenters.push_back(sf::Glsl::Vec3(sphere.center.x, sphere.center.y, sphere.center.z));
            sphereRadii.push_back(sphere.radius);
            
            // Material properties
            sphereColors.push_back(sf::Glsl::Vec3(
                sphere.material.colour.x, 
                sphere.material.colour.y, 
                sphere.material.colour.z));
                
            sphereEmissionColors.push_back(sf::Glsl::Vec3(
                sphere.material.emissionColour.x,
                sphere.material.emissionColour.y,
                sphere.material.emissionColour.z));
                
            sphereSpecularColors.push_back(sf::Glsl::Vec3(
                sphere.material.specularColour.x,
                sphere.material.specularColour.y,
                sphere.material.specularColour.z));
                
            sphereEmissionStrengths.push_back(sphere.material.emissionStrength);
            sphereSmoothness.push_back(sphere.material.smoothness);
            sphereSpecularProbs.push_back(sphere.material.specularProbability);
        }
        
        // Pass arrays to shader
        shader.setUniformArray("sphereCenters", sphereCenters.data(), sphereCenters.size());
        shader.setUniformArray("sphereRadii", sphereRadii.data(), sphereRadii.size());
        
        // Pass material properties
        shader.setUniformArray("sphereColors", sphereColors.data(), sphereColors.size());
        shader.setUniformArray("sphereEmissionColors", sphereEmissionColors.data(), sphereEmissionColors.size());
        shader.setUniformArray("sphereSpecularColors", sphereSpecularColors.data(), sphereSpecularColors.size());
        shader.setUniformArray("sphereEmissionStrengths", sphereEmissionStrengths.data(), sphereEmissionStrengths.size());
        shader.setUniformArray("sphereSmoothness", sphereSmoothness.data(), sphereSmoothness.size());
        shader.setUniformArray("sphereSpecularProbs", sphereSpecularProbs.data(), sphereSpecularProbs.size());

        // Draw with shader
        window.draw(fullscreenQuad, &shader);
        window.display();
    }

    return 0;
}