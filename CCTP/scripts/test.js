// Test runner script
const { exec } = require('child_process');

console.log('🚀 Starting CCTP Transfer Burn tests...');
console.log('📡 Forking BASE mainnet...');

// Set environment variables for testing
process.env.BASE_RPC_URL = process.env.BASE_RPC_URL || 'https://mainnet.base.org';

exec('npx hardhat test', (error, stdout, stderr) => {
  if (error) {
    console.error(`❌ Test execution error: ${error}`);
    return;
  }
  if (stderr) {
    console.error(`⚠️  Test stderr: ${stderr}`);
  }
  console.log(`✅ Test output:\n${stdout}`);
});
