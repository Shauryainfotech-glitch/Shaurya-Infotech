import { google } from 'googleapis';
import { Readable } from 'stream';

export class GoogleDriveService {
  private drive: any;
  private auth: any;

  constructor() {
    // Initialize Google Drive API
    this.auth = new google.auth.GoogleAuth({
      keyFile: process.env.GOOGLE_SERVICE_ACCOUNT_KEY, // Path to service account key
      scopes: ['https://www.googleapis.com/auth/drive'],
    });
    
    this.drive = google.drive({ version: 'v3', auth: this.auth });
  }

  // Create a folder in Google Drive
  async createFolder(name: string, parentFolderId?: string): Promise<{ id: string; webViewLink: string }> {
    try {
      const fileMetadata: any = {
        name: name,
        mimeType: 'application/vnd.google-apps.folder',
      };

      if (parentFolderId) {
        fileMetadata.parents = [parentFolderId];
      }

      const response = await this.drive.files.create({
        resource: fileMetadata,
        fields: 'id, webViewLink',
      });

      return {
        id: response.data.id,
        webViewLink: response.data.webViewLink,
      };
    } catch (error) {
      console.error('Error creating folder:', error);
      throw new Error(`Failed to create folder: ${error}`);
    }
  }

  // Upload file to Google Drive
  async uploadFile(
    fileName: string,
    fileBuffer: Buffer,
    mimeType: string,
    folderId?: string
  ): Promise<{ id: string; webViewLink: string; downloadLink: string }> {
    try {
      const fileMetadata: any = {
        name: fileName,
      };

      if (folderId) {
        fileMetadata.parents = [folderId];
      }

      const media = {
        mimeType: mimeType,
        body: Readable.from(fileBuffer),
      };

      const response = await this.drive.files.create({
        resource: fileMetadata,
        media: media,
        fields: 'id, webViewLink',
      });

      // Make file publicly viewable (optional)
      await this.drive.permissions.create({
        fileId: response.data.id,
        resource: {
          role: 'reader',
          type: 'anyone',
        },
      });

      const downloadLink = `https://drive.google.com/uc?id=${response.data.id}`;

      return {
        id: response.data.id,
        webViewLink: response.data.webViewLink,
        downloadLink: downloadLink,
      };
    } catch (error) {
      console.error('Error uploading file:', error);
      throw new Error(`Failed to upload file: ${error}`);
    }
  }

  // Get file metadata
  async getFileMetadata(fileId: string) {
    try {
      const response = await this.drive.files.get({
        fileId: fileId,
        fields: 'id, name, size, mimeType, modifiedTime, createdTime, webViewLink',
      });

      return response.data;
    } catch (error) {
      console.error('Error getting file metadata:', error);
      throw new Error(`Failed to get file metadata: ${error}`);
    }
  }

  // Download file from Google Drive
  async downloadFile(fileId: string): Promise<Buffer> {
    try {
      const response = await this.drive.files.get({
        fileId: fileId,
        alt: 'media',
      });

      return Buffer.from(response.data);
    } catch (error) {
      console.error('Error downloading file:', error);
      throw new Error(`Failed to download file: ${error}`);
    }
  }

  // Delete file from Google Drive
  async deleteFile(fileId: string): Promise<void> {
    try {
      await this.drive.files.delete({
        fileId: fileId,
      });
    } catch (error) {
      console.error('Error deleting file:', error);
      throw new Error(`Failed to delete file: ${error}`);
    }
  }

  // List files in a folder
  async listFiles(folderId?: string, pageSize: number = 10) {
    try {
      const query = folderId ? `'${folderId}' in parents` : undefined;
      
      const response = await this.drive.files.list({
        q: query,
        pageSize: pageSize,
        fields: 'nextPageToken, files(id, name, size, mimeType, modifiedTime, webViewLink)',
      });

      return response.data.files || [];
    } catch (error) {
      console.error('Error listing files:', error);
      throw new Error(`Failed to list files: ${error}`);
    }
  }

  // Update file permissions
  async updatePermissions(fileId: string, permissions: Array<{ role: string; type: string; emailAddress?: string }>) {
    try {
      for (const permission of permissions) {
        await this.drive.permissions.create({
          fileId: fileId,
          resource: permission,
        });
      }
    } catch (error) {
      console.error('Error updating permissions:', error);
      throw new Error(`Failed to update permissions: ${error}`);
    }
  }

  // Search files
  async searchFiles(query: string, pageSize: number = 10) {
    try {
      const response = await this.drive.files.list({
        q: query,
        pageSize: pageSize,
        fields: 'nextPageToken, files(id, name, size, mimeType, modifiedTime, webViewLink)',
      });

      return response.data.files || [];
    } catch (error) {
      console.error('Error searching files:', error);
      throw new Error(`Failed to search files: ${error}`);
    }
  }
}

export const googleDriveService = new GoogleDriveService();