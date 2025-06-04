import { Request, Response } from 'express';
import { tenderOCRProcessor } from './tender-ocr-processor';

// Test endpoint for OCR processing with GeM document
export async function testOCREndpoint(req: Request, res: Response) {
  try {
    // Sample GeM bidding document text (extracted from your PDF)
    const gemDocumentText = `
Bid Number/बोली मांक ( बड सं या) : GEM/2025/B/6171965
Dated/ दनांक : 25-04-2025

Bid End Date/Time/ बड बंद होने क तार ख/समय: 16-05-2025 09:00:00
Bid Opening Date/Time/ बड खुलने क तार ख/समय: 16-05-2025 09:30:00

Ministry/State Name/मं ालय/रा य का नाम: Ministry Of Defence
Department Name/ वभाग का नाम: Department Of Military Affairs
Organisation Name/संगठन का नाम: Indian Air Force

Item Category/मद केटे गर: Repair and Overhauling Service - built up trucks; Ashok leyland; Yes; Buyer Premises
Contract Period/अनुबंध अविध: 1 Month(s) 13 Day(s)

Technical Specifications/तकनीक विश याँ
Product Category: built up trucks
Product Brand: Ashok leyland
Spares Required: Yes
Place of Repair/Maintenance: Buyer Premises
Product Details: LORRY 6.5 TON 4X4

Consignees/Reporting Officer/परे षती/ रपो टग अिधकार
Address/पता: Jaisalmer
Number of Products to be Repaired: 3
`;

    console.log('Processing GeM document with OCR...');
    
    // Extract data using OCR processor
    const extractedData = await tenderOCRProcessor.processGeMLBiddingDocument(gemDocumentText);
    
    console.log('Extracted data:', extractedData);
    
    // Create tender from extracted data
    const createdTender = await tenderOCRProcessor.createTenderFromExtractedData(extractedData);
    
    res.json({
      success: true,
      message: 'GeM document processed successfully and tender created',
      extractedData: {
        bidNumber: extractedData.bidNumber,
        title: extractedData.title,
        ministry: extractedData.ministry,
        department: extractedData.department,
        organisation: extractedData.organisation,
        bidEndDate: extractedData.bidEndDate,
        estimatedValue: extractedData.estimatedValue,
        location: extractedData.location,
        itemCategory: extractedData.itemCategory
      },
      createdTender: {
        id: createdTender.id,
        tenderId: createdTender.tenderId,
        title: createdTender.title,
        departmentName: createdTender.departmentName,
        organization: createdTender.organization,
        value: createdTender.value,
        deadline: createdTender.deadline,
        tenderType: createdTender.tenderType,
        status: createdTender.status
      },
      autoTenderCreation: true
    });
    
  } catch (error) {
    console.error('OCR test failed:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to process GeM document',
      error: error.message
    });
  }
}