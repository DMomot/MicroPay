import React from 'react'
import { useAccount, useConnect, useDisconnect, useEnsName } from 'wagmi'

export function WalletConnection() {
  const { address, isConnected } = useAccount()
  const { data: ensName } = useEnsName({ address })
  const { connect, connectors, error, isLoading, pendingConnector } = useConnect()
  const { disconnect } = useDisconnect()

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  }

  if (isConnected) {
    return (
      <div className="wallet-connected">
        <div className="wallet-info">
          <span className="wallet-address">
            {ensName ? ensName : formatAddress(address!)}
          </span>
          <button onClick={() => disconnect()} className="disconnect-button">
            Отключить
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="wallet-connection">
      <div className="wallet-connectors">
        {connectors.map((connector) => (
          <button
            disabled={!connector.ready}
            key={connector.id}
            onClick={() => connect({ connector })}
            className="connect-button"
          >
            {connector.name}
            {!connector.ready && ' (не поддерживается)'}
            {isLoading &&
              connector.id === pendingConnector?.id &&
              ' (подключение...)'}
          </button>
        ))}
      </div>

      {error && <div className="connection-error">{error.message}</div>}
    </div>
  )
}
