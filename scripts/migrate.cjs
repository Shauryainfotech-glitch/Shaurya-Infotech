const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// Function to execute shell commands
function execCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error}`);
        reject(error);
        return;
      }
      console.log(stdout);
      if (stderr) console.error(stderr);
      resolve(stdout);
    });
  });
}

async function runMigration() {
  try {
    // Ensure migrations directory exists
    const migrationsDir = path.join(process.cwd(), 'migrations');
    if (!fs.existsSync(migrationsDir)) {
      fs.mkdirSync(migrationsDir, { recursive: true });
    }

    // Generate migrations
    console.log('Generating migrations...');
    await execCommand('npx drizzle-kit generate:pg');

    // Push schema changes to database
    console.log('Pushing schema changes...');
    await execCommand('npx drizzle-kit push:pg');

    console.log('Migration completed successfully');
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

runMigration();
