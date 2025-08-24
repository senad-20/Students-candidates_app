<?php

function admin_login_form() {
    if (is_user_logged_in()) {
        return '<p>Vous êtes déjà connecté.</p>';
    }

    ob_start();

    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['ambassade_login'])) {
        $pseudo = sanitize_user($_POST['pseudo']);
        $mdp = $_POST['mdp'];

        $creds = [
            'user_login'    => $pseudo,
            'user_password' => $mdp,
            'remember'      => true
        ];

        $user = wp_signon($creds, false);

        if (is_wp_error($user)) {
            echo '<p style="color:red;">Connexion échouée : ' . $user->get_error_message() . '</p>';
        } else {
            wp_redirect(admin_url()); // redirige vers le tableau de bord WordPress
            exit;
        }
    }

    ?>

    <form method="post">
        <label for="pseudo">Nom d’utilisateur :</label><br>
        <input type="text" name="pseudo" required><br><br>

        <label for="mdp">Mot de passe :</label><br>
        <input type="password" name="mdp" required><br><br>

        <input type="submit" name="ambassade_login" value="Se connecter">
    </form>

    <?php

    return ob_get_clean();
}

add_shortcode('admin_login', 'ambassade_admin_login_form');
