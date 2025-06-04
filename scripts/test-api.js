import fetch from 'node-fetch';

const BASE_URL = 'http://localhost:3000/api';

async function testEndpoints() {
  try {
    console.log('Starting API tests...\n');

    // Test creating a tender
    console.log('Testing POST /tenders');
    const createResponse = await fetch(`${BASE_URL}/tenders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: 'Test Tender',
        departmentName: 'Test Department',
        organization: 'Test Organization',
        description: 'Test Description',
        tenderType: 'Open',
        value: '₹1,00,000',
        deadline: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
        status: 'Draft'
      })
    });

    if (!createResponse.ok) {
      throw new Error(`Failed to create tender: ${createResponse.statusText}`);
    }

    const createdTender = await createResponse.json();
    console.log('Created tender:', createdTender);
    console.log('✓ Create tender test passed\n');

    // Test getting all tenders
    console.log('Testing GET /tenders');
    const listResponse = await fetch(`${BASE_URL}/tenders`);
    
    if (!listResponse.ok) {
      throw new Error(`Failed to list tenders: ${listResponse.statusText}`);
    }

    const tenders = await listResponse.json();
    console.log(`Retrieved ${tenders.length} tenders`);
    console.log('✓ List tenders test passed\n');

    // Test getting a single tender
    console.log(`Testing GET /tenders/${createdTender.id}`);
    const getResponse = await fetch(`${BASE_URL}/tenders/${createdTender.id}`);
    
    if (!getResponse.ok) {
      throw new Error(`Failed to get tender: ${getResponse.statusText}`);
    }

    const tender = await getResponse.json();
    console.log('Retrieved tender:', tender);
    console.log('✓ Get tender test passed\n');

    // Test updating a tender
    console.log(`Testing PUT /tenders/${createdTender.id}`);
    const updateResponse = await fetch(`${BASE_URL}/tenders/${createdTender.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...tender,
        title: 'Updated Test Tender',
        status: 'In Progress'
      })
    });

    if (!updateResponse.ok) {
      throw new Error(`Failed to update tender: ${updateResponse.statusText}`);
    }

    const updatedTender = await updateResponse.json();
    console.log('Updated tender:', updatedTender);
    console.log('✓ Update tender test passed\n');

    // Test deleting a tender
    console.log(`Testing DELETE /tenders/${createdTender.id}`);
    const deleteResponse = await fetch(`${BASE_URL}/tenders/${createdTender.id}`, {
      method: 'DELETE'
    });

    if (!deleteResponse.ok) {
      throw new Error(`Failed to delete tender: ${deleteResponse.statusText}`);
    }

    console.log('✓ Delete tender test passed\n');

    console.log('All API tests passed successfully! ✨');

  } catch (error) {
    console.error('Test failed:', error.message);
    process.exit(1);
  }
}

// Run the tests
testEndpoints();
