#include <SFML/Graphics.hpp>

int main()
{
    // Create window with SFML 3.0 syntax
    //sf::RenderWindow window(sf::VideoMode({800, 600}), "GLSL Shader Demo", sf::State::Windowed);
    sf::RenderWindow window(sf::VideoMode::getFullscreenModes().front(), "GLSL Shader Demo", sf::State::Fullscreen);
    window.setFramerateLimit(60);

    // Load fragment shader
    sf::Shader shader;
    if (!shader.loadFromFile("../src/marioshader.frag", sf::Shader::Type::Fragment))
    {
        return -1;
    }

    // Create fullscreen rectangle
    sf::RectangleShape fullscreenQuad(sf::Vector2f(window.getSize()));

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
        // Handle events using new callback style
        window.handleEvents(
            [&](const sf::Event::Closed&) { window.close(); },
            [](const auto&) {} // Catch-all for other events
        );

        // Update shader uniforms
        shader.setUniform("time", clock.getElapsedTime().asSeconds());
        shader.setUniform("resolution", sf::Vector2f(window.getSize()));

        // Draw with shader
        window.clear(sf::Color::Black);
        window.draw(fullscreenQuad, &shader);
        window.display();
    }

    return 0;
}