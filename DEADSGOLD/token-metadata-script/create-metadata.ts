import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { createSignerFromKeypair, signerIdentity, publicKey, percentAmount } from '@metaplex-foundation/umi';
import { createV1, mplTokenMetadata, TokenStandard, findMetadataPda } from '@metaplex-foundation/mpl-token-metadata';
import * as fs from 'fs';

async function main() {
    console.log('Starting metadata creation script...');

    // 1. Initialize Umi with Solana devnet connection
    const umi = createUmi('https://api.devnet.solana.com');
    umi.use(mplTokenMetadata());

    // 2. Load your keypair
    const keypairPath = '/home/deadsg/.config/solana/new-dev-wallet.json';
    let secretKey: Uint8Array;
    try {
        secretKey = new Uint8Array(JSON.parse(fs.readFileSync(keypairPath, 'utf-8')));
    } catch (error) {
        console.error(`Error reading keypair file at ${keypairPath}:`, error);
        return;
    }
    const keypair = umi.eddsa.createKeypairFromSecretKey(secretKey);
    umi.use(signerIdentity(createSignerFromKeypair(umi, keypair)));
    console.log(`Keypair loaded for public key: ${umi.identity.publicKey}`);

    // 3. Define token details
    const mintAddress = publicKey('HPUj1r6RLnWuP63a6H2D2DgEGfUAL3Bw9woC7xBt3kLj'); // Your token's mint address
    const tokenName = 'DEADSGOLD';
    const tokenSymbol = 'DEAD';
    const tokenUri = 'https://example.com/deadsgold-metadata.json'; // Placeholder URI - UPDATE THIS LATER!
    console.log(`Token Mint Address: ${mintAddress}`);
    console.log(`Token Name: ${tokenName}`);
    console.log(`Token Symbol: ${tokenSymbol}`);
    console.log(`Token URI: ${tokenUri}`);

    // 4. Derive the metadata PDA
    const metadataPda = findMetadataPda(umi, { mint: mintAddress });
    console.log(`Derived Metadata Account PDA: ${metadataPda}`);

    // 5. Create the metadata account
    try {
        console.log('Sending createV1 transaction...');
        const { signature } = await createV1(umi, {
            metadata: metadataPda,
            mint: mintAddress,
            authority: umi.identity,
            payer: umi.identity,
            updateAuthority: umi.identity,
            name: tokenName,
            symbol: tokenSymbol,
            uri: tokenUri,
            sellerFeeBasisPoints: percentAmount(0),
            creators: null,
            collection: null,
            uses: null,
            tokenStandard: TokenStandard.Fungible,
        }).sendAndConfirm(umi);

        console.log(`Successfully created metadata for token: ${tokenName}`);
        console.log(`Transaction signature: ${signature}`);
        console.log(`Metadata Account PDA: ${metadataPda}`);
        console.log(`Remember to update the tokenUri (${tokenUri}) with the actual URL of your uploaded metadata JSON.`);

    } catch (error) {
        console.error('Error creating metadata:', error);
        if (error instanceof Error) {
            console.error('Error message:', error.message);
            console.error('Error stack:', error.stack);
        }
    }
}

main();