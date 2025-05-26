import crypto from 'crypto';

interface BlockchainRecord {
  id: string;
  timestamp: Date;
  tenderId: number;
  action: string;
  data: any;
  hash: string;
  previousHash: string;
  signature: string;
  verified: boolean;
}

interface TenderBlock {
  index: number;
  timestamp: Date;
  tenderId: number;
  data: {
    action: string;
    details: any;
    submittedBy: string;
    ipfsHash?: string;
  };
  hash: string;
  previousHash: string;
  nonce: number;
  merkleRoot: string;
}

export class BlockchainService {
  private chain: TenderBlock[] = [];
  private pendingTransactions: any[] = [];
  private miningReward = 100;

  constructor() {
    // Create genesis block
    this.chain = [this.createGenesisBlock()];
  }

  createGenesisBlock(): TenderBlock {
    const genesisBlock: TenderBlock = {
      index: 0,
      timestamp: new Date(),
      tenderId: 0,
      data: {
        action: 'genesis',
        details: 'TenderAI Pro Blockchain Genesis Block',
        submittedBy: 'system'
      },
      hash: '',
      previousHash: '0',
      nonce: 0,
      merkleRoot: ''
    };
    
    genesisBlock.hash = this.calculateHash(genesisBlock);
    return genesisBlock;
  }

  getLatestBlock(): TenderBlock {
    return this.chain[this.chain.length - 1];
  }

  // Record tender submission on blockchain
  async recordTenderSubmission(tenderId: number, submissionData: any, submittedBy: string): Promise<string> {
    const blockData = {
      action: 'tender_submission',
      details: {
        tenderId,
        title: submissionData.title,
        value: submissionData.value,
        deadline: submissionData.deadline,
        submissionHash: this.generateDataHash(submissionData)
      },
      submittedBy,
      timestamp: new Date().toISOString()
    };

    const newBlock = this.createNewBlock(tenderId, blockData);
    this.addBlock(newBlock);
    
    return newBlock.hash;
  }

  // Record document upload with IPFS hash
  async recordDocumentUpload(tenderId: number, documentData: any, uploadedBy: string): Promise<string> {
    const ipfsHash = this.simulateIPFSUpload(documentData);
    
    const blockData = {
      action: 'document_upload',
      details: {
        tenderId,
        documentName: documentData.name,
        documentType: documentData.type,
        fileSize: documentData.size,
        documentHash: this.generateDataHash(documentData)
      },
      submittedBy: uploadedBy,
      ipfsHash,
      timestamp: new Date().toISOString()
    };

    const newBlock = this.createNewBlock(tenderId, blockData);
    this.addBlock(newBlock);
    
    return newBlock.hash;
  }

  // Record tender award decision
  async recordTenderAward(tenderId: number, awardData: any, awardedBy: string): Promise<string> {
    const blockData = {
      action: 'tender_award',
      details: {
        tenderId,
        awardedTo: awardData.awardedTo,
        awardValue: awardData.value,
        awardDate: awardData.date,
        evaluationScore: awardData.score
      },
      submittedBy: awardedBy,
      timestamp: new Date().toISOString()
    };

    const newBlock = this.createNewBlock(tenderId, blockData);
    this.addBlock(newBlock);
    
    return newBlock.hash;
  }

  // Verify tender record integrity
  verifyTenderRecord(tenderId: number): {
    isValid: boolean;
    records: TenderBlock[];
    auditTrail: string[];
  } {
    const tenderBlocks = this.chain.filter(block => block.tenderId === tenderId);
    const auditTrail: string[] = [];
    
    let isValid = true;
    
    for (let i = 0; i < tenderBlocks.length; i++) {
      const block = tenderBlocks[i];
      const recalculatedHash = this.calculateHash(block);
      
      if (block.hash !== recalculatedHash) {
        isValid = false;
        auditTrail.push(`❌ Block ${block.index} hash verification failed`);
      } else {
        auditTrail.push(`✅ Block ${block.index} verified: ${block.data.action}`);
      }
    }

    return {
      isValid,
      records: tenderBlocks,
      auditTrail
    };
  }

  // Generate digital signature for tender documents
  generateDigitalSignature(data: any, privateKey?: string): string {
    const dataString = JSON.stringify(data);
    const hash = crypto.createHash('sha256').update(dataString).digest('hex');
    
    // In production, use actual digital signing with private keys
    const signature = crypto.createHash('sha256').update(hash + (privateKey || 'default-key')).digest('hex');
    
    return signature;
  }

  // Verify digital signature
  verifyDigitalSignature(data: any, signature: string, publicKey?: string): boolean {
    const expectedSignature = this.generateDigitalSignature(data, publicKey || 'default-key');
    return signature === expectedSignature;
  }

  // Create smart contract for tender compliance
  createTenderSmartContract(tenderId: number, rules: any): {
    contractId: string;
    rules: any;
    status: string;
  } {
    const contractId = this.generateContractId(tenderId);
    
    const contract = {
      contractId,
      tenderId,
      rules: {
        eligibilityRequirements: rules.eligibility || [],
        documentRequirements: rules.documents || [],
        deadlines: rules.deadlines || {},
        complianceChecks: rules.compliance || []
      },
      status: 'active',
      createdAt: new Date().toISOString()
    };

    // Record contract creation on blockchain
    const blockData = {
      action: 'smart_contract_created',
      details: contract,
      submittedBy: 'system',
      timestamp: new Date().toISOString()
    };

    const newBlock = this.createNewBlock(tenderId, blockData);
    this.addBlock(newBlock);

    return contract;
  }

  // Get complete audit trail for tender
  getTenderAuditTrail(tenderId: number): {
    totalBlocks: number;
    timeline: Array<{
      timestamp: Date;
      action: string;
      details: any;
      blockHash: string;
      verified: boolean;
    }>;
    integrity: boolean;
  } {
    const tenderBlocks = this.chain.filter(block => block.tenderId === tenderId);
    const verification = this.verifyTenderRecord(tenderId);
    
    const timeline = tenderBlocks.map(block => ({
      timestamp: block.timestamp,
      action: block.data.action,
      details: block.data.details,
      blockHash: block.hash,
      verified: verification.isValid
    }));

    return {
      totalBlocks: tenderBlocks.length,
      timeline,
      integrity: verification.isValid
    };
  }

  // Private helper methods
  private createNewBlock(tenderId: number, data: any): TenderBlock {
    const previousBlock = this.getLatestBlock();
    const newBlock: TenderBlock = {
      index: previousBlock.index + 1,
      timestamp: new Date(),
      tenderId,
      data,
      hash: '',
      previousHash: previousBlock.hash,
      nonce: 0,
      merkleRoot: this.calculateMerkleRoot([data])
    };

    newBlock.hash = this.mineBlock(newBlock, 2); // Difficulty level 2
    return newBlock;
  }

  private addBlock(newBlock: TenderBlock): void {
    this.chain.push(newBlock);
  }

  private calculateHash(block: TenderBlock): string {
    return crypto.createHash('sha256').update(
      block.index + 
      block.timestamp.toISOString() + 
      block.previousHash + 
      JSON.stringify(block.data) + 
      block.nonce +
      block.merkleRoot
    ).digest('hex');
  }

  private mineBlock(block: TenderBlock, difficulty: number): string {
    const target = Array(difficulty + 1).join('0');
    
    while (block.hash.substring(0, difficulty) !== target) {
      block.nonce++;
      block.hash = this.calculateHash(block);
    }
    
    return block.hash;
  }

  private calculateMerkleRoot(transactions: any[]): string {
    if (transactions.length === 0) return '';
    if (transactions.length === 1) {
      return crypto.createHash('sha256').update(JSON.stringify(transactions[0])).digest('hex');
    }

    const hashes = transactions.map(tx => 
      crypto.createHash('sha256').update(JSON.stringify(tx)).digest('hex')
    );

    while (hashes.length > 1) {
      const newHashes = [];
      for (let i = 0; i < hashes.length; i += 2) {
        const left = hashes[i];
        const right = hashes[i + 1] || left;
        const combined = crypto.createHash('sha256').update(left + right).digest('hex');
        newHashes.push(combined);
      }
      hashes.splice(0, hashes.length, ...newHashes);
    }

    return hashes[0];
  }

  private generateDataHash(data: any): string {
    return crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex');
  }

  private generateContractId(tenderId: number): string {
    const timestamp = Date.now().toString();
    return crypto.createHash('sha256').update(`contract_${tenderId}_${timestamp}`).digest('hex').substring(0, 16);
  }

  private simulateIPFSUpload(data: any): string {
    // Simulate IPFS hash generation
    const hash = crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex');
    return `Qm${hash.substring(0, 44)}`;
  }

  // Public blockchain query methods
  getBlockchainStats(): {
    totalBlocks: number;
    totalTenders: number;
    latestBlock: TenderBlock;
    chainIntegrity: boolean;
  } {
    const uniqueTenders = new Set(this.chain.map(block => block.tenderId));
    
    return {
      totalBlocks: this.chain.length,
      totalTenders: uniqueTenders.size - 1, // Exclude genesis block
      latestBlock: this.getLatestBlock(),
      chainIntegrity: this.validateChain()
    };
  }

  private validateChain(): boolean {
    for (let i = 1; i < this.chain.length; i++) {
      const currentBlock = this.chain[i];
      const previousBlock = this.chain[i - 1];

      if (currentBlock.hash !== this.calculateHash(currentBlock)) {
        return false;
      }

      if (currentBlock.previousHash !== previousBlock.hash) {
        return false;
      }
    }
    return true;
  }
}

export const blockchainService = new BlockchainService();