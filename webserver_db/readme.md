# Setup Instructions for Raspberry Pi with MariaDB and phpMyAdmin

1. **Prepare the SSH Public Key:**
   - Generate or locate the SSH public key from the machine you will use to connect to the Raspberry Pi.

2. **Prepare the OS:**
   - Flash the OS onto the SD card.
   - Set up the WiFi password so the Raspberry Pi can connect automatically on boot.
   - Paste the SSH public key into the OS setup and deactivate password-based SSH connections.

3. **Find the Raspberry Pi IP Address:**
   - Scan your network to find the IP address of your Raspberry Pi.
   - SSH into the Raspberry Pi using the found IP address.

4. **Update and Upgrade the Raspberry Pi:**
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo apt install mariadb-server
   ```

5. **Secure MariaDB Installation:**
   ```bash
   sudo mysql_secure_installation 
   ```

6. **Verify MariaDB Installation:**
   - Connect to MariaDB using the root user (no password required):
   ```bash
   sudo mysql -u root
   ```

7. **Install phpMyAdmin:**
   ```bash
   sudo apt install phpmyadmin
   ```
   - During installation, choose "yes" for all prompts.
   - Use the password: `***l3tm31n###***`

8. **Configure Database Access:**
   - Connect to MariaDB using the root user:
   ```bash
   sudo mysql -u root
   ```
   - Enter the following command to grant privileges:
   ```sql
   GRANT ALL PRIVILEGES ON *.* TO 'raspoutine'@'localhost' IDENTIFIED BY 'l3tm31in###' WITH GRANT OPTION;
   ```

9. **Configure Apache for phpMyAdmin:**
   - Edit the Apache configuration file:
   ```bash
   sudo vim /etc/apache2/apache2.conf
   ```
   - Add the following line at the end of the file:
   ```
   Include /etc/phpmyadmin/apache.conf
   ```

10. **Restart Apache to Apply Changes:**
    ```bash
    sudo service apache2 restart
    ```

11. **Make phpMyAdmin Accessible:**
    - Create a symlink to make phpMyAdmin accessible via the web server:
    ```bash
    sudo ln -s /usr/share/phpmyadmin /var/www/html
    ```

12. **Access phpMyAdmin:**
    - Connect to the database on the Raspberry Pi using the credentials: `raspoutine:l3tm31n###`


