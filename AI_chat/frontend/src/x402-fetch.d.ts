declare module 'x402-fetch' {
  import { WalletClient } from 'viem';
  
  export function wrapFetchWithPayment(
    fetchFn: typeof fetch,
    walletClient: WalletClient
  ): typeof fetch;
  
  export function decodeXPaymentResponse(response: any): any;
}

declare module 'x402-axios' {
  import { AxiosInstance } from 'axios';
  
  export function withPaymentInterceptor(
    axiosInstance: AxiosInstance,
    config: {
      wallet: {
        address: string;
        signTypedData: (typedData: any) => Promise<string>;
      };
    }
  ): AxiosInstance;
  
  export function decodeXPaymentResponse(response: any): any;
}
