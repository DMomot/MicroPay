# CCTP Transfer and Burn Contract

🚀 Простой контракт для выполнения EIP3009 transfer и CCTP burn в одной транзакции на BASE сети.

## ✨ Функциональность

- **transferAndBurn**: Основной метод, который выполняет:
  1. EIP3009 transferWithAuthorization - переводит USDC от пользователя на контракт
  2. CCTP burn - сжигает полученные токены через TokenMinter
- **emergencyWithdraw**: Функция восстановления для owner'а

## 🛠 Установка и запуск

```bash
# Установка зависимостей
npm install

# Компиляция контрактов
npx hardhat compile

# Запуск тестов (форк BASE сети)
npm run test

# Запуск упрощенных тестов
npx hardhat test test/CCTPTransferBurn.simple.test.js
```

## 📋 Адреса контрактов BASE

- **USDC**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **CCTP TokenMinter**: `0x1682Ae6375C4E4A97e4B583BC394c861A46D8962`

## 🧪 Тестирование

### Упрощенные тесты (работают сразу)
```bash
npx hardhat test test/CCTPTransferBurn.simple.test.js --verbose
```

Эти тесты проверяют:
- ✅ Деплой контракта
- ✅ Правильность адресов
- ✅ Создание EIP3009 подписи
- ✅ Базовую функциональность

### Полные тесты с форком BASE
```bash
npx hardhat test test/CCTPTransferBurn.test.js
```

Эти тесты включают:
- 🔄 Форк BASE mainnet
- 💰 Пополнение баланса USDC
- ✍️ Подписание EIP3009 авторизации
- 🔥 Выполнение transferAndBurn

## 🔧 Использование

1. **Деплой контракта**:
   ```solidity
   CCTPTransferBurn cctp = new CCTPTransferBurn(
       USDC_ADDRESS,
       TOKEN_MINTER_ADDRESS
   );
   ```

2. **Создание EIP3009 подписи**:
   ```javascript
   const signature = await user._signTypedData(domain, types, value);
   const { v, r, s } = ethers.utils.splitSignature(signature);
   ```

3. **Выполнение transferAndBurn**:
   ```javascript
   await cctp.transferAndBurn(
       from, amount, validAfter, validBefore, nonce, v, r, s
   );
   ```

## 🔒 Безопасность

- ✅ ReentrancyGuard для защиты от реентрантности
- ✅ Ownable для контроля доступа
- ✅ Emergency функция для восстановления токенов
- ✅ Валидация EIP3009 подписей

## 📁 Структура проекта

```
CCTP/                             # Hardhat проект
├── contracts/
│   ├── CCTPTransferBurn.sol      # Основной контракт
│   └── interfaces/
│       ├── IEIP3009.sol          # EIP3009 интерфейс
│       └── ITokenMinter.sol      # CCTP интерфейс
├── test/
│   ├── CCTPTransferBurn.test.js        # Полные тесты
│   └── CCTPTransferBurn.simple.test.js # Упрощенные тесты
├── hardhat.config.js             # Конфигурация с форком BASE
└── package.json                  # Зависимости
```

## 🎯 MVP готов к использованию!

Контракт протестирован и готов для интеграции в ScoutPay систему.
