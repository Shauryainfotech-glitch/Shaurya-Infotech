import { tenderOCRProcessor } from './tender-ocr-processor';
import { storage } from './storage';

// GeM bidding document content extracted from the PDF
const gemBiddingText = `
Bid Number/बोली मांक ( बड सं या) : GEM/2025/B/6171965
Dated/ दनांक : 25-04-2025

Bid Document/ बड द तावेज़

Bid Details/ बड ववरण

Bid End Date/Time/ बड बंद होने क तार ख/समय: 16-05-2025 09:00:00
Bid Opening Date/Time/ बड खुलने क तार ख/समय: 16-05-2025 09:30:00
Bid Offer Validity (From End Date)/ बड पेशकश वैधता (बंद होने क तार ख से): 180 (Days)

Ministry/State Name/मं ालय/रा य का नाम: Ministry Of Defence
Department Name/ वभाग का नाम: Department Of Military Affairs
Organisation Name/संगठन का नाम: Indian Air Force
Office Name/कायालय का नाम: ***********
े ता ईमेल/Buyer Email: success.road@gov.in

Item Category/मद केटे गर: Repair and Overhauling Service - built up trucks; Ashok leyland; Yes; Buyer Premises
Contract Period/अनुबंध अविध: 1 Month(s) 13 Day(s)

MSE Exemption for Years Of Experience/अनुभव के वष से एमएसई छूट/ and Turnover/टनओवर के िलए एमएसई को छूट ा है: Yes
Startup Exemption for Years Of Experience/अनुभव के वष से टाटअप छूट/ and Turnover/ टनओवर के िलए टाटअप को छूट ा है: Yes

Document required from seller/ व े ता से मांगे गए द तावेज़: Experience Criteria,Bidder Turnover,Certificate (Requested in ATC)
*In case any bidder is seeking exemption from Experience / Turnover Criteria, the supporting documents to prove his eligibility for exemption must be uploaded for evaluation by the buyer

Do you want to show documents uploaded by bidders to all bidders participated in bid?: No
Bid to RA enabled/ बड से रवस नीलामी स य कया: Yes
RA Qualification Rule: H1-Highest Priced Bid Elimination
Type of Bid/ बड का कार: Two Packet Bid

Time allowed for Technical Clarifications during technical evaluation/तकनीक मू यांकन के दौरान तकनीक प ीकरण हे तु अनुमत समय: 2 Days
Evaluation Method/मू यांकन प ित: Total value wise evaluation

Financial Document Indicating Price Breakup Required/मू य दश ने वाला व ीय द तावेज ेकअप आव यक है: Yes
Arbitration Clause: No
Mediation Clause: No

EMD Detail/ईएमड ववरण
Required/आव यकता: No

ePBG Detail/ईपीबीजी ववरण
Required/आव यकता: No

MII Compliance/एमआईआई अनुपालन
MII Compliance/एमआईआई अनुपालन: Yes

MSE Purchase Preference/एमएसई खर द वर यता
MSE Purchase Preference/एमएसई खर द वर यता: Yes

Repair And Overhauling Service - Built Up Trucks; Ashok Leyland; Yes; Buyer Premises (3)

Technical Specifications/तकनीक विश याँ

Specification                                                 Values
Core
Product Category                                              built up trucks
Product Brand                                                 Ashok leyland
Spares Required                                               Yes
Place of Repair/Maintenance                                   Buyer Premises

Additional Details/अित र ववरण
Product Details                                               LORRY 6.5 TON 4X4

Consignees/Reporting Officer/परे षती/ रपो टग अिधकार

S.No./ . सं.    Consignee Reporting/Officer/ परे षती/ रपो टग अिधकार    Address/पता              Number of Products to be Repaired    Additional Requirement/अित र आव यकता
1               ***********                                            ***********Jaisalmer     3                                     N/A

Buyer Added Bid Specific Terms and Conditions/ े ता ारा जोड़ गई बड क वशेष शत
1. Buyer Added Bid Specific Scope Of Work(SOW)
File Attachment Click here to view the file .
`;

export async function testOCRWithGeMLDocument() {
  console.log('Starting OCR test with GeM bidding document...');
  
  try {
    // Process the GeM document text
    const extractedData = await tenderOCRProcessor.processGeMLBiddingDocument(gemBiddingText);
    
    console.log('Extracted Data:', JSON.stringify(extractedData, null, 2));
    
    // Create tender from extracted data
    const createdTender = await tenderOCRProcessor.createTenderFromExtractedData(extractedData);
    
    console.log('Created Tender:', JSON.stringify(createdTender, null, 2));
    
    return {
      success: true,
      extractedData,
      createdTender,
      message: 'GeM document processed successfully and tender created'
    };
    
  } catch (error) {
    console.error('OCR test failed:', error);
    return {
      success: false,
      error: error.message,
      message: 'Failed to process GeM document'
    };
  }
}

// Export for testing
export default testOCRWithGeMLDocument;