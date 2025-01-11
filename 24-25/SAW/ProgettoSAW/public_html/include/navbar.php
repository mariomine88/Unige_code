<nav class="navbar navbar-expand-lg navbar-dark bg-dark py-2">
    <div class="container">
        <!-- Logo and Brand -->
        <a class="navbar-brand d-flex align-items-center" href="index.php" aria-label="Threadit Home">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-chat-square-text" viewBox="0 0 16 16">
                <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1h-2.5a2 2 0 0 0-1.6.8L8 14.333 6.1 11.8a2 2 0 0 0-1.6-.8H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2.5a1 1 0 0 1 .8.4l1.9 2.533a1 1 0 0 0 1.6 0l1.9-2.533a1 1 0 0 1 .8-.4H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
                <path d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6zm0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"/>
            </svg>
            <span class="fw-bold d-none d-md-inline ms-2">Threadit</span>
        </a>

        <!-- Search Bar -->
        <?php if (isset($_SESSION["user_username"])) : ?>
        <div class="d-flex flex-grow-1 px-md-4 mx-md-4 mx-2">
            <form class="w-100" action="../pages/search.php" method="GET">
                <div class="input-group">
                    <input type="text" class="form-control bg-light" placeholder="Search" name="search">
                    <button class="btn btn-outline-light" type="submit" aria-label="Search">
                        <i class="bi bi-search"></i>
                        <span class="d-none d-md-inline ms-1">Search</span>
                    </button>
                </div>
            </form>
        </div>
        <?php endif; ?>

        <!-- Navigation Items -->
        <div class="d-flex align-items-center">
            <?php if (isset($_SESSION["user_username"])) : ?>
                <a href="create_post.php<?php echo isset($community['name']) ? '?community_name=' . urlencode($community['name']) : ''; ?>" 
                   class="btn btn-primary btn-sm me-2" 
                   aria-label="Create Post">
                    <i class="bi bi-plus-lg"></i>
                    <span class="d-none d-md-inline">Create Post</span>
                </a>
                <?php if(isset($_SESSION["is_admin"]) && $_SESSION["is_admin"]): ?>
                    <a href="create_community.php" class="btn btn-primary btn-sm me-2" aria-label="Create Community">
                        <i class="bi bi-plus-lg"></i>
                        <span class="d-none d-md-inline">Create Community</span>
                    </a>
                <?php endif; ?>
                <div class="dropdown">
                    <button class="btn btn-dark profile-btn d-flex align-items-center justify-content-center" type="button" data-bs-toggle="dropdown" aria-label="Profile Menu">
                        <i class="bi bi-person-circle"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                        <li>
                            <div class="dropdown-header user-header">
                                <i class="bi bi-person-circle"></i>
                                <a href="./public_profile.php?UID=<?= htmlspecialchars($_SESSION["user_username"]) ?>">
                                <span><?= htmlspecialchars($_SESSION["user_username"]) ?></span>
                                </a>
                            </div>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="../BackEnd/show_profile.php" aria-label="Edit Profile">Edit</a></li>
                        <li><a class="dropdown-item text-danger" href="../BackEnd/logout.php" aria-label="Log Out">Log Out</a></li>
                    </ul>
                </div>
            <?php else : ?>
                <a href="login.php" class="btn btn-secondary btn-sm me-2" aria-label="Log In">Log In</a>
                <a href="signup.php" class="btn btn-primary btn-sm" aria-label="Sign Up">Sign Up</a>
            <?php endif; ?>
        </div>
    </div>
</nav>