/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

// Manufacturing Requisitions JavaScript

class ManufacturingRequisitionWidget extends Component {
    setup() {
        // Initialize manufacturing requisition widget
    }
    
    onEmergencyRequisition() {
        // Handle emergency requisition creation
        console.log('Emergency requisition triggered');
    }
    
    onShopFloorUpdate() {
        // Handle shop floor updates
        console.log('Shop floor update triggered');
    }
}

ManufacturingRequisitionWidget.template = "manufacturing_material_requisitions.ManufacturingRequisitionWidget";

registry.category("fields").add("manufacturing_requisition_widget", ManufacturingRequisitionWidget);

// Shop Floor Integration
class ShopFloorIntegration {
    constructor() {
        this.terminal_id = null;
        this.operator_id = null;
    }
    
    initializeTerminal(terminal_id) {
        this.terminal_id = terminal_id;
        console.log(`Shop floor terminal ${terminal_id} initialized`);
    }
    
    createEmergencyRequisition(data) {
        // Create emergency requisition from shop floor
        return this._rpc({
            model: 'shop.floor.requisition',
            method: 'create_emergency_requisition',
            args: [data.machine_id, data.operator_id, data.materials, data.impact]
        });
    }
    
    scanBarcode(barcode) {
        // Handle barcode scanning
        console.log(`Barcode scanned: ${barcode}`);
    }
}

// Export for global use
window.ShopFloorIntegration = ShopFloorIntegration; 