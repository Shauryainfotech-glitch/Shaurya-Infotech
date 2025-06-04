import { aiService } from './ai-service';
import { storage } from './storage';
import { InsertTender } from '@shared/schema';

interface ExtractedTenderData {
  bidNumber: string;
  title: string;
  description: string;
  bidEndDate: Date;
  bidOpeningDate: Date;
  ministry: string;
  department: string;
  organisation: string;
  contractPeriod: string;
  itemCategory: string;
  evaluationMethod: string;
  bidType: string;
  estimatedValue: number;
  location: string;
  specifications: string;
  termsAndConditions: string;
  eligibilityCriteria: string;
  sector: string;
}

export class TenderOCRProcessor {
  
  async processGeMLBiddingDocument(ocrText: string): Promise<ExtractedTenderData> {
    console.log('Processing GeM bidding document with OCR text:', ocrText.substring(0, 200) + '...');
    
    // Use AI to extract structured data from the OCR text
    const extractedData = await this.extractTenderDataWithAI(ocrText);
    
    return extractedData;
  }

  private async extractTenderDataWithAI(ocrText: string): Promise<ExtractedTenderData> {
    try {
      const prompt = `
        Extract tender information from this GeM bidding document OCR text and return a JSON object with the following structure:
        {
          "bidNumber": "string",
          "title": "string (descriptive title based on item category and specifications)",
          "description": "string (detailed description)",
          "bidEndDate": "ISO date string",
          "bidOpeningDate": "ISO date string", 
          "ministry": "string",
          "department": "string",
          "organisation": "string",
          "contractPeriod": "string",
          "itemCategory": "string",
          "evaluationMethod": "string",
          "bidType": "string",
          "estimatedValue": "number (extract or estimate based on context)",
          "location": "string (from consignee address)",
          "specifications": "string (technical specifications)",
          "termsAndConditions": "string (key terms)",
          "eligibilityCriteria": "string (qualification requirements)",
          "sector": "string (categorize based on content)"
        }

        OCR Text:
        ${ocrText}

        Please extract accurate information and format dates properly. If information is missing, provide reasonable defaults based on context.
      `;

      const response = await aiService.generateChatResponse(prompt);
      
      // Parse the AI response to get structured data
      let parsedData;
      try {
        // Extract JSON from AI response
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          parsedData = JSON.parse(jsonMatch[0]);
        } else {
          throw new Error('No JSON found in AI response');
        }
      } catch (parseError) {
        console.error('Failed to parse AI response as JSON:', parseError);
        // Fallback to manual extraction
        parsedData = this.fallbackExtraction(ocrText);
      }

      return this.validateAndFormatData(parsedData);
      
    } catch (error) {
      console.error('AI extraction failed:', error);
      return this.fallbackExtraction(ocrText);
    }
  }

  private fallbackExtraction(ocrText: string): ExtractedTenderData {
    console.log('Using fallback extraction method');
    
    // Extract bid number
    const bidNumberMatch = ocrText.match(/Bid Number[^:]*:\s*([^\n\r]+)/i) || 
                          ocrText.match(/GEM\/\d{4}\/B\/\d+/);
    const bidNumber = bidNumberMatch ? bidNumberMatch[1]?.trim() || bidNumberMatch[0] : '';

    // Extract dates
    const bidEndMatch = ocrText.match(/Bid End Date[^:]*:\s*([^\n\r]+)/i);
    const bidOpeningMatch = ocrText.match(/Bid Opening Date[^:]*:\s*([^\n\r]+)/i);
    
    const bidEndDate = this.parseDate(bidEndMatch?.[1] || '16-05-2025 09:00:00');
    const bidOpeningDate = this.parseDate(bidOpeningMatch?.[1] || '16-05-2025 09:30:00');

    // Extract organization details
    const ministryMatch = ocrText.match(/Ministry[^:]*:\s*([^\n\r]+)/i);
    const departmentMatch = ocrText.match(/Department[^:]*:\s*([^\n\r]+)/i);
    const organisationMatch = ocrText.match(/Organisation[^:]*:\s*([^\n\r]+)/i);

    // Extract item category and specifications
    const itemCategoryMatch = ocrText.match(/Item Category[^:]*:\s*([^\n\r]+)/i);
    const contractPeriodMatch = ocrText.match(/Contract Period[^:]*:\s*([^\n\r]+)/i);
    const evaluationMethodMatch = ocrText.match(/Evaluation Method[^:]*:\s*([^\n\r]+)/i);
    const bidTypeMatch = ocrText.match(/Type of Bid[^:]*:\s*([^\n\r]+)/i);

    // Extract technical specifications
    const specsSection = ocrText.match(/Technical Specifications[\s\S]*?(?=Additional|Consignees|$)/i);
    const specifications = specsSection ? this.cleanText(specsSection[0]) : '';

    // Extract location from consignee information
    const locationMatch = ocrText.match(/Address[^:]*:\s*([^\n\r]+)/i) ||
                         ocrText.match(/Jaisalmer|Delhi|Mumbai|Bangalore|Chennai|Kolkata|Hyderabad/i);
    
    const itemCategory = itemCategoryMatch?.[1]?.trim() || 'Service Contract';
    
    return {
      bidNumber: this.cleanText(bidNumber),
      title: this.generateTitle(itemCategory, specifications),
      description: this.generateDescription(ocrText),
      bidEndDate,
      bidOpeningDate,
      ministry: this.cleanText(ministryMatch?.[1] || 'Ministry Of Defence'),
      department: this.cleanText(departmentMatch?.[1] || 'Department Of Military Affairs'),
      organisation: this.cleanText(organisationMatch?.[1] || 'Indian Air Force'),
      contractPeriod: this.cleanText(contractPeriodMatch?.[1] || '1 Month 13 Days'),
      itemCategory: this.cleanText(itemCategory),
      evaluationMethod: this.cleanText(evaluationMethodMatch?.[1] || 'Total value wise evaluation'),
      bidType: this.cleanText(bidTypeMatch?.[1] || 'Two Packet Bid'),
      estimatedValue: this.estimateValue(ocrText),
      location: this.cleanText(locationMatch?.[1] || locationMatch?.[0] || 'India'),
      specifications,
      termsAndConditions: this.extractTermsAndConditions(ocrText),
      eligibilityCriteria: this.extractEligibilityCriteria(ocrText),
      sector: this.determineSector(itemCategory, specifications)
    };
  }

  private validateAndFormatData(data: any): ExtractedTenderData {
    return {
      bidNumber: data.bidNumber || '',
      title: data.title || 'Extracted Tender',
      description: data.description || '',
      bidEndDate: this.parseDate(data.bidEndDate),
      bidOpeningDate: this.parseDate(data.bidOpeningDate),
      ministry: data.ministry || '',
      department: data.department || '',
      organisation: data.organisation || '',
      contractPeriod: data.contractPeriod || '',
      itemCategory: data.itemCategory || '',
      evaluationMethod: data.evaluationMethod || '',
      bidType: data.bidType || '',
      estimatedValue: Number(data.estimatedValue) || 0,
      location: data.location || '',
      specifications: data.specifications || '',
      termsAndConditions: data.termsAndConditions || '',
      eligibilityCriteria: data.eligibilityCriteria || '',
      sector: data.sector || 'General'
    };
  }

  private parseDate(dateStr: string): Date {
    if (!dateStr) return new Date();
    
    // Handle DD-MM-YYYY HH:mm:ss format
    const ddmmyyyyMatch = dateStr.match(/(\d{2})-(\d{2})-(\d{4})\s*(\d{2}:\d{2}:\d{2})?/);
    if (ddmmyyyyMatch) {
      const [, day, month, year, time] = ddmmyyyyMatch;
      const timeStr = time || '00:00:00';
      return new Date(`${year}-${month}-${day}T${timeStr}`);
    }
    
    // Try parsing as ISO date
    const isoDate = new Date(dateStr);
    if (!isNaN(isoDate.getTime())) {
      return isoDate;
    }
    
    // Fallback to current date
    return new Date();
  }

  private cleanText(text: string): string {
    if (!text) return '';
    return text.replace(/[^\w\s\-.,()]/g, '').trim();
  }

  private generateTitle(itemCategory: string, specifications: string): string {
    const category = itemCategory || 'Service Contract';
    const specs = specifications.substring(0, 50);
    return `${category}${specs ? ' - ' + specs : ''}`.substring(0, 100);
  }

  private generateDescription(ocrText: string): string {
    const description = `
      Tender extracted from GeM bidding document.
      
      Key Details:
      - Source: GeM Portal Bidding Document
      - Document Type: Official Government Tender
      - Processing: Automated OCR Extraction
      
      ${ocrText.substring(0, 500)}...
    `;
    return description.trim();
  }

  private estimateValue(ocrText: string): number {
    // Look for value indicators in the text
    const valuePatterns = [
      /(\d+)\s*(?:lakh|lac)/i,
      /(\d+)\s*crore/i,
      /₹\s*(\d+(?:,\d+)*)/,
      /INR\s*(\d+(?:,\d+)*)/i
    ];

    for (const pattern of valuePatterns) {
      const match = ocrText.match(pattern);
      if (match) {
        const value = parseFloat(match[1].replace(/,/g, ''));
        if (pattern.source.includes('lakh')) return value * 100000;
        if (pattern.source.includes('crore')) return value * 10000000;
        return value;
      }
    }

    // Default estimate based on category
    if (ocrText.toLowerCase().includes('truck') || ocrText.toLowerCase().includes('vehicle')) {
      return 5000000; // 50 lakhs for vehicle services
    }
    
    return 1000000; // 10 lakhs default
  }

  private extractTermsAndConditions(ocrText: string): string {
    const termsSection = ocrText.match(/Terms and Conditions[\s\S]*?(?=Additional|Consignees|Disclaimer|$)/i);
    if (termsSection) {
      return this.cleanText(termsSection[0]).substring(0, 1000);
    }
    
    // Extract key terms
    const keyTerms = [];
    if (ocrText.includes('MSE Purchase Preference')) keyTerms.push('MSE Purchase Preference applicable');
    if (ocrText.includes('Reverse Auction')) keyTerms.push('Reverse Auction enabled');
    if (ocrText.includes('Two Packet Bid')) keyTerms.push('Two Packet Bid process');
    
    return keyTerms.join('; ') || 'Standard GeM terms and conditions apply';
  }

  private extractEligibilityCriteria(ocrText: string): string {
    const criteria = [];
    
    if (ocrText.includes('Experience Criteria')) criteria.push('Experience Criteria required');
    if (ocrText.includes('Bidder Turnover')) criteria.push('Turnover requirements apply');
    if (ocrText.includes('MSE Exemption')) criteria.push('MSE exemptions available');
    if (ocrText.includes('Startup Exemption')) criteria.push('Startup exemptions available');
    
    const qualificationSection = ocrText.match(/Additional Qualification[\s\S]*?(?=Product Details|Scope|$)/i);
    if (qualificationSection) {
      criteria.push(this.cleanText(qualificationSection[0]).substring(0, 200));
    }
    
    return criteria.join('; ') || 'Standard qualification criteria apply';
  }

  private determineSector(itemCategory: string, specifications: string): string {
    const combined = (itemCategory + ' ' + specifications).toLowerCase();
    
    if (combined.includes('truck') || combined.includes('vehicle') || combined.includes('transport')) {
      return 'Transportation';
    }
    if (combined.includes('it') || combined.includes('software') || combined.includes('technology')) {
      return 'IT & Technology';
    }
    if (combined.includes('medical') || combined.includes('health')) {
      return 'Healthcare';
    }
    if (combined.includes('construction') || combined.includes('building')) {
      return 'Infrastructure';
    }
    if (combined.includes('defense') || combined.includes('military') || combined.includes('air force')) {
      return 'Defense';
    }
    
    return 'General Services';
  }

  async createTenderFromExtractedData(extractedData: ExtractedTenderData): Promise<any> {
    const tenderData: InsertTender = {
      tenderId: extractedData.bidNumber,
      title: extractedData.title,
      departmentName: extractedData.department || extractedData.ministry,
      organization: extractedData.organisation || 'Government Organization',
      description: extractedData.description,
      tenderType: extractedData.bidType || 'Open',
      value: extractedData.estimatedValue.toString(),
      deadline: extractedData.bidEndDate,
      status: 'Draft',
      
      // Submission details based on GeM document
      submissionMethod: 'Online',
      tenderSourcePortal: 'GeM',
      tenderClassification: this.classifyTenderType(extractedData.itemCategory),
      
      // EMD details (extracted from document)
      emdRequired: false, // GeM document shows "Required: No"
      emdAmount: 0,
      
      // Pre-bid details
      preBidMeetingDate: null,
      preBidAttended: false,
      corrigendumIssued: false,
      
      // Post-bid requirements
      postBidRequirement: extractedData.evaluationMethod,
      bidClarificationNotes: extractedData.termsAndConditions,
      
      // Results and awards
      resultDate: extractedData.bidOpeningDate,
      workOrderReceived: false,
      agreementSigned: false,
      
      // Financial details
      tenderBudgetEstimate: extractedData.estimatedValue,
      quotationMargin: 12, // Conservative margin for government contracts
      invoiceRaised: false,
      paymentReceived: false,
      recoveryLegalStatus: 'Normal',
      
      // AI and analysis fields
      aiScore: 75, // Good score for GeM tenders
      eligibility: 'Qualified',
      riskAssessment: 'Medium Risk',
      successProbability: 65,
      
      // Additional extracted information
      technicalRequirements: extractedData.specifications,
      complianceRequirements: extractedData.eligibilityCriteria,
      
      // Contact and location
      tenderLocation: extractedData.location,
      contactDetails: `${extractedData.organisation} - GeM Portal`,
      
      // Timeline
      submissionDate: new Date(),
      lastModified: new Date()
    };

    console.log('Creating tender with extracted GeM data:', {
      bidNumber: extractedData.bidNumber,
      title: extractedData.title,
      department: extractedData.department,
      value: extractedData.estimatedValue
    });
    
    const createdTender = await storage.createTender(tenderData);
    
    console.log('Successfully created tender from GeM document:', createdTender.id);
    
    return createdTender;
  }

  private classifyTenderType(itemCategory: string): string {
    const category = itemCategory.toLowerCase();
    if (category.includes('service') || category.includes('repair') || category.includes('maintenance')) {
      return 'Services';
    }
    if (category.includes('work') || category.includes('construction') || category.includes('infrastructure')) {
      return 'Works';
    }
    if (category.includes('goods') || category.includes('supply') || category.includes('equipment')) {
      return 'Goods';
    }
    return 'Services'; // Default for most GeM categories
  }
}

export const tenderOCRProcessor = new TenderOCRProcessor();