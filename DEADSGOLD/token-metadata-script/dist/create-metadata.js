"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const umi_bundle_defaults_1 = require("@metaplex-foundation/umi-bundle-defaults");
const umi_1 = require("@metaplex-foundation/umi");
const mpl_token_metadata_1 = require("@metaplex-foundation/mpl-token-metadata");
const fs = __importStar(require("fs"));
async function main() {
    console.log('Starting metadata creation script...');
    // 1. Initialize Umi with Solana devnet connection
    const umi = (0, umi_bundle_defaults_1.createUmi)('https://api.devnet.solana.com');
    umi.use((0, mpl_token_metadata_1.mplTokenMetadata)());
    // 2. Load your keypair
    const keypairPath = '/home/deadsg/.config/solana/new-dev-wallet.json';
    let secretKey;
    try {
        secretKey = new Uint8Array(JSON.parse(fs.readFileSync(keypairPath, 'utf-8')));
    }
    catch (error) {
        console.error(`Error reading keypair file at ${keypairPath}:`, error);
        return;
    }
    const keypair = umi.eddsa.createKeypairFromSecretKey(secretKey);
    umi.use((0, umi_1.signerIdentity)((0, umi_1.createSignerFromKeypair)(umi, keypair)));
    console.log(`Keypair loaded for public key: ${umi.identity.publicKey}`);
    // 3. Define token details
    const mintAddress = (0, umi_1.publicKey)('HPUj1r6RLnWuP63a6H2D2DgEGfUAL3Bw9woC7xBt3kLj'); // Your token's mint address
    const tokenName = 'DEADSGOLD';
    const tokenSymbol = 'DEAD';
    const tokenUri = 'https://example.com/deadsgold-metadata.json'; // Placeholder URI - UPDATE THIS LATER!
    console.log(`Token Mint Address: ${mintAddress}`);
    console.log(`Token Name: ${tokenName}`);
    console.log(`Token Symbol: ${tokenSymbol}`);
    console.log(`Token URI: ${tokenUri}`);
    // 4. Derive the metadata PDA
    const metadataPda = (0, mpl_token_metadata_1.findMetadataPda)(umi, { mint: mintAddress });
    console.log(`Derived Metadata Account PDA: ${metadataPda}`);
    // 5. Create the metadata account
    try {
        console.log('Sending createV1 transaction...');
        const { signature } = await (0, mpl_token_metadata_1.createV1)(umi, {
            metadata: metadataPda,
            mint: mintAddress,
            authority: umi.identity,
            payer: umi.identity,
            updateAuthority: umi.identity,
            name: tokenName,
            symbol: tokenSymbol,
            uri: tokenUri,
            sellerFeeBasisPoints: (0, umi_1.percentAmount)(0),
            creators: null,
            collection: null,
            uses: null,
            tokenStandard: mpl_token_metadata_1.TokenStandard.Fungible,
        }).sendAndConfirm(umi);
        console.log(`Successfully created metadata for token: ${tokenName}`);
        console.log(`Transaction signature: ${signature}`);
        console.log(`Metadata Account PDA: ${metadataPda}`);
        console.log(`Remember to update the tokenUri (${tokenUri}) with the actual URL of your uploaded metadata JSON.`);
    }
    catch (error) {
        console.error('Error creating metadata:', error);
        if (error instanceof Error) {
            console.error('Error message:', error.message);
            console.error('Error stack:', error.stack);
        }
    }
}
main();
