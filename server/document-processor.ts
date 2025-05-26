import sharp from 'sharp';
import pdfParse from 'pdf-parse';
import { googleDriveService } from './google-drive';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export class DocumentProcessor {
  // Process uploaded file and extract content
  async processDocument(file: Buffer, mimeType: string, fileName: string) {
    const result = {
      content: '',
      ocrText: '',
      extractedMetadata: {},
      thumbnailUrl: '',
      processedSuccessfully: false,
      error: null as string | null,
    };

    try {
      // Extract text content based on file type
      if (mimeType === 'application/pdf') {
        const pdfData = await pdfParse(file);
        result.content = pdfData.text;
        result.extractedMetadata = {
          pages: pdfData.numpages,
          info: pdfData.info,
          version: pdfData.version,
        };
      }
      
      // Process images with OpenAI Vision for OCR and analysis
      if (mimeType.startsWith('image/')) {
        // Generate thumbnail
        const thumbnail = await sharp(file)
          .resize(300, 300, { fit: 'inside' })
          .jpeg({ quality: 80 })
          .toBuffer();
        
        // Use OpenAI Vision API for intelligent OCR and document analysis
        const base64Image = file.toString('base64');
        const visionResponse = await openai.chat.completions.create({
          model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "Extract all text from this document image and analyze it for tender-related information. Identify key details like tender numbers, deadlines, requirements, and compliance certificates."
                },
                {
                  type: "image_url",
                  image_url: {
                    url: `data:${mimeType};base64,${base64Image}`
                  }
                }
              ],
            },
          ],
          max_tokens: 1000,
        });

        result.ocrText = visionResponse.choices[0].message.content || '';
        result.content = result.ocrText;
        result.extractedMetadata = {
          format: mimeType,
          hasImage: true,
          aiProcessed: true,
        };
      }

      // Process Word documents (would need additional libraries)
      if (mimeType.includes('word') || mimeType.includes('document')) {
        result.content = 'Document text extraction would be implemented here';
        result.extractedMetadata = {
          format: mimeType,
          documentType: 'word',
        };
      }

      result.processedSuccessfully = true;
    } catch (error) {
      result.error = `Failed to process document: ${error}`;
      console.error('Document processing error:', error);
    }

    return result;
  }

  // Upload document to Google Drive and process
  async uploadAndProcess(
    file: Buffer,
    fileName: string,
    mimeType: string,
    tenderId?: number,
    folderId?: string
  ) {
    try {
      // Process document first
      const processedDoc = await this.processDocument(file, mimeType, fileName);

      // Upload to Google Drive
      const driveResult = await googleDriveService.uploadFile(
        fileName,
        file,
        mimeType,
        folderId
      );

      return {
        ...processedDoc,
        googleDriveFileId: driveResult.id,
        googleDriveUrl: driveResult.webViewLink,
        downloadLink: driveResult.downloadLink,
      };
    } catch (error) {
      throw new Error(`Failed to upload and process document: ${error}`);
    }
  }

  // Create tender-specific folder structure in Google Drive
  async createTenderFolderStructure(tenderTitle: string, tenderId: number) {
    try {
      // Create main tender folder
      const mainFolder = await googleDriveService.createFolder(`Tender_${tenderId}_${tenderTitle}`);
      
      // Create subfolders
      const subfolders = [
        'Proposal Documents',
        'Technical Documentation',
        'Compliance Certificates',
        'Financial Documents',
        'Legal Documents',
        'Communication',
      ];

      const createdFolders = {
        mainFolder: mainFolder,
        subfolders: {} as Record<string, any>,
      };

      for (const folderName of subfolders) {
        const subfolder = await googleDriveService.createFolder(folderName, mainFolder.id);
        createdFolders.subfolders[folderName] = subfolder;
      }

      return createdFolders;
    } catch (error) {
      throw new Error(`Failed to create folder structure: ${error}`);
    }
  }

  // Validate document compliance
  validateCompliance(documentType: string, extractedContent: string) {
    const compliance = {
      isCompliant: false,
      issues: [] as string[],
      score: 0,
      recommendations: [] as string[],
    };

    // Basic compliance checks based on document type
    switch (documentType) {
      case 'Proposal Document':
        if (!extractedContent.toLowerCase().includes('proposal')) {
          compliance.issues.push('Document may not be a valid proposal');
        }
        if (!extractedContent.toLowerCase().includes('price') && !extractedContent.toLowerCase().includes('cost')) {
          compliance.issues.push('No pricing information found');
        }
        break;
        
      case 'Affidavit/Declaration':
        if (!extractedContent.toLowerCase().includes('hereby declare') && !extractedContent.toLowerCase().includes('affidavit')) {
          compliance.issues.push('Document may not be a valid affidavit/declaration');
        }
        break;
        
      case 'Test Reports':
        if (!extractedContent.toLowerCase().includes('test') && !extractedContent.toLowerCase().includes('report')) {
          compliance.issues.push('Document may not be a valid test report');
        }
        break;
    }

    // Calculate compliance score
    compliance.score = Math.max(0, 100 - (compliance.issues.length * 25));
    compliance.isCompliant = compliance.score >= 75;

    // Generate recommendations
    if (compliance.issues.length > 0) {
      compliance.recommendations.push('Review document content for completeness');
      compliance.recommendations.push('Ensure all required sections are included');
    }

    return compliance;
  }

  // Extract key information using OpenAI for intelligent document analysis
  async extractKeyInformation(content: string, documentType: string) {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4o", // the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        messages: [
          {
            role: "system",
            content: "You are an expert tender document analyst. Extract key information from tender documents and provide structured analysis in JSON format."
          },
          {
            role: "user",
            content: `Analyze this ${documentType} document and extract key information. Provide response in JSON format with the following structure:
            {
              "summary": "Brief summary of the document",
              "keyDates": ["List of important dates found"],
              "requirements": ["List of key requirements"],
              "riskFactors": ["Potential risks or challenges"],
              "complianceItems": ["Compliance requirements and certificates needed"],
              "eligibilityCriteria": ["Eligibility requirements"],
              "technicalSpecs": ["Technical specifications if any"],
              "financialRequirements": ["Financial requirements like EMD, turnover criteria"],
              "entities": ["Important entities mentioned"],
              "keyPhrases": ["Key phrases and terms"],
              "sentiment": "overall sentiment of document",
              "importantDates": ["Critical dates and deadlines"],
              "amounts": ["Financial amounts mentioned"]
            }
            
            Document content: ${content}`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 1500,
      });

      const analysis = JSON.parse(response.choices[0].message.content || '{}');
      
      // Return in expected format with fallbacks
      return {
        entities: analysis.entities || [],
        keyPhrases: analysis.keyPhrases || [],
        sentiment: analysis.sentiment || 'neutral',
        summary: analysis.summary || '',
        importantDates: analysis.importantDates || [],
        amounts: analysis.amounts || [],
        requirements: analysis.requirements || [],
        riskFactors: analysis.riskFactors || [],
        complianceItems: analysis.complianceItems || [],
        eligibilityCriteria: analysis.eligibilityCriteria || [],
        technicalSpecs: analysis.technicalSpecs || [],
        financialRequirements: analysis.financialRequirements || []
      };
    } catch (error) {
      console.error('Error extracting key information:', error);
      return {
        entities: [],
        keyPhrases: [],
        sentiment: 'neutral',
        summary: 'Analysis unavailable',
        importantDates: [],
        amounts: [],
        requirements: [],
        riskFactors: [],
        complianceItems: [],
        eligibilityCriteria: [],
        technicalSpecs: [],
        financialRequirements: []
      };
    }
  }
}

export const documentProcessor = new DocumentProcessor();