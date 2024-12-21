<form class="form register" action="Registrazione.php" method="POST">
  <span class="input-span">
    <label for="nome" class="label">Nome</label>
    <input type="text" name="nome" id="nome" required />
  </span>
  <span class="input-span">
    <label for="cognome" class="label">Cognome</label>
    <input type="text" name="cognome" id="cognome" required />
  </span>
  <span class="input-span">
    <label for="email" class="label">Email</label>
    <input type="email" name="email" id="email" required />
  </span>
  <span class="input-span">
    <label for="password" class="label">Password</label>
    <input type="password" name="password" id="password" required />
  </span>
  <span class="input-span">
    <label for="confirm-password" class="label">Conferma Password</label>
    <input type="password" name="confirm-password" id="confirm-password" required />
  </span>
  <input class="submit" type="submit" value="Registrati" />
</form>