#include <SFML/Graphics.hpp>
#include <SFML/System/Vector3.hpp>
#include <vector>

struct vec3 {
    float x, y, z;
    
    vec3(float x, float y, float z) : x(x), y(y), z(z) {}
};

struct Sphere {
    vec3 center;
    float radius;
    
    Sphere(const vec3& c, float r) : center(c), radius(r) {}
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

    // Create multiple spheres
    std::vector<Sphere> spheres;
    spheres.push_back(Sphere(vec3(0.0f, 0.0f, -5.0f), 1.0f));     // First sphere
    spheres.push_back(Sphere(vec3(2.0f, 0.5f, -6.0f), 0.7f));     // Second sphere

    // Define maximum number of spheres (must match shader)
    const int MAX_SPHERES = 10;

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
        
        // Fill arrays with sphere data
        for (const auto& sphere : spheres) {
            sphereCenters.push_back(sf::Glsl::Vec3(sphere.center.x, sphere.center.y, sphere.center.z));
            sphereRadii.push_back(sphere.radius);
        }
        
        // Pass arrays to shader
        shader.setUniformArray("sphereCenters", sphereCenters.data(), sphereCenters.size());
        shader.setUniformArray("sphereRadii", sphereRadii.data(), sphereRadii.size());

        // Draw with shader
        window.draw(fullscreenQuad, &shader);
        window.display();
    }

    return 0;
}