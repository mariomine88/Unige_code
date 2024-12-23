<?php
require_once 'config_session.php';

session_unset();
session_destroy();

header("Location: ../index.php");
die();
