import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { createSignerFromKeypair, signerIdentity, publicKey, percentAmount } from '@metaplex-foundation/umi';
import { updateV1, mplTokenMetadata, TokenStandard, findMetadataPda, fetchMetadata } from '@metaplex-foundation/mpl-token-metadata';
import * as fs from 'fs';

async function main() {
    console.log('Starting metadata update script...');

    // 1. Initialize Umi with Solana Mainnet-beta connection
    const umi = createUmi('https://api.mainnet-beta.solana.com');
    umi.use(mplTokenMetadata());

    // 2. Load your keypair
    const keypairPath = '/home/deadsg/.config/solana/new-dev-wallet.json'; // Ensure this path is correct for your setup
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
    const newTokenUri = 'https://ipfs.io/ipfs/QmRyEpCAXB5rc78SLCXtLifwRQGuKmhuyQVD8XzPWCwRKm'; // Your new IPFS metadata URI
    console.log(`Token Mint Address: ${mintAddress}`);
    console.log(`New Token URI: ${newTokenUri}`);

    // 4. Derive the metadata PDA
    const metadataPda = findMetadataPda(umi, { mint: mintAddress });
    console.log(`Derived Metadata Account PDA: ${metadataPda}`);

    // 5. Fetch existing metadata
    console.log('Fetching existing metadata...');
    const oldMetadata = await fetchMetadata(umi, metadataPda);
    console.log('Existing metadata fetched.');

    // 6. Update the metadata account
    try {
        console.log('Sending updateV1 transaction...');
        const { signature } = await updateV1(umi, {
            metadata: metadataPda,
            mint: mintAddress,
            authority: umi.identity,
            newUpdateAuthority: umi.identity.publicKey, // Keep the same update authority
            data: {
                name: oldMetadata.name, // Use existing name
                symbol: oldMetadata.symbol, // Use existing symbol
                uri: newTokenUri, // Update URI
                sellerFeeBasisPoints: oldMetadata.sellerFeeBasisPoints, // Use existing sellerFeeBasisPoints
                creators: oldMetadata.creators, // Use existing creators
            },
            primarySaleHappened: oldMetadata.primarySaleHappened, // Use existing value
            isMutable: oldMetadata.isMutable, // Use existing value
        }).sendAndConfirm(umi);

        console.log(`Successfully updated metadata for token: ${oldMetadata.name}`);
        console.log(`Transaction signature: ${signature}`);
        console.log(`Metadata Account PDA: ${metadataPda}`);

    } catch (error) {
        console.error('Error updating metadata:', error);
        if (error instanceof Error) {
            console.error('Error message:', error.message);
            console.error('Error stack:', error.stack);
        }
    }
}

main();
