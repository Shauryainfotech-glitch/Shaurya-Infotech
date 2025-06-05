def migrate(cr, version):
    if not version:
        return

    # Add any necessary post-migration operations here
    # For example, updating data or computing fields
    cr.execute("""
        -- Update any necessary data
        UPDATE mrp_estimation
        SET state = 'draft'
        WHERE state IS NULL;
        
        -- Ensure all records have a sequence number
        UPDATE mrp_estimation e
        SET name = 'EST/' || TO_CHAR(NOW(), 'YYYY/MM') || '/' || LPAD(ROW_NUMBER() OVER (ORDER BY id)::text, 4, '0')
        WHERE name IS NULL;
    """) 