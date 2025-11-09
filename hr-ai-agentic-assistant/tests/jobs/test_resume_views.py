from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import Applicant
import tempfile
import os
import json


class ResumeApplicantUploadViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('applicant_upload')

    def test_get_resume_upload_page(self):
        """Test that the resume upload page loads correctly"""
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resume Upload')

    def test_post_valid_pdf_upload(self):
        """Test uploading a valid PDF file"""
        # Create a simple PDF-like file with sufficient size (>1KB)
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [3 0 R]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>' + b'x' * 1024  # Add extra data to ensure >1KB
        pdf_file = SimpleUploadedFile("test_resume.pdf", pdf_content, content_type="application/pdf")

        response = self.client.post(self.upload_url, {'resume_files': [pdf_file]}, format='multipart')
        
        # The response should be JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    def test_post_valid_docx_upload(self):
        """Test uploading a valid DOCX file"""
        # Create a simple DOCX-like file with sufficient size (>1KB)
        docx_content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00' + b'x' * 1024  # Start of a ZIP file + extra data to ensure >1KB
        docx_file = SimpleUploadedFile("test_resume.docx", docx_content, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = self.client.post(self.upload_url, {'resume_files': [docx_file]}, format='multipart')
        
        # The response should be JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    def test_post_invalid_file_type(self):
        """Test uploading an invalid file type"""
        # Create a text file with sufficient size (>1KB)
        txt_content = b'This is a text file' + b'x' * 1024  # Add extra data to ensure >1KB
        txt_file = SimpleUploadedFile("test_resume.txt", txt_content, content_type="text/plain")

        response = self.client.post(self.upload_url, {'resume_files': [txt_file]}, format='multipart')
        
        # The response should be JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # The first result should have an error status
        self.assertEqual(response_data['results'][0]['status'], 'error')

    def test_post_large_file(self):
        """Test uploading a file larger than 10MB limit"""
        # Create a large file (>10MB)
        large_content = b'0' * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile("large_resume.pdf", large_content, content_type="application/pdf")

        response = self.client.post(self.upload_url, {'resume_files': [large_file]}, format='multipart')
        
        # The response should be JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # The first result should have an error status due to size
        self.assertEqual(response_data['results'][0]['status'], 'error')

    def test_resume_duplicate_content_detection(self):
        """Test that duplicate resume content is detected"""
        # Create first file with sufficient size (>1KB)
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Size 2\n/Root 1 0 R\n>>' + b'x' * 1024  # Add extra data to ensure >1KB
        pdf_file1 = SimpleUploadedFile("test_resume1.pdf", pdf_content, content_type="application/pdf")

        # Upload first file
        response1 = self.client.post(self.upload_url, {'resume_files': [pdf_file1]}, format='multipart')
        response_data1 = json.loads(response1.content)
        self.assertTrue(response_data1['success'])
        self.assertEqual(response_data1['results'][0]['status'], 'success')

        # Upload same content again as second file
        pdf_file2 = SimpleUploadedFile("test_resume2.pdf", pdf_content, content_type="application/pdf")
        
        response2 = self.client.post(self.upload_url, {'resume_files': [pdf_file2]}, format='multipart')
        response_data2 = json.loads(response2.content)
        self.assertTrue(response_data2['success'])
        # Should detect it as duplicate
        self.assertEqual(response_data2['results'][0]['status'], 'duplicate')

    def test_resume_duplicate_name_detection(self):
        """Test that duplicate resume names are detected"""
        # Create two different files with same name pattern, with sufficient size (>1KB)
        pdf_content1 = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Size 2\n/Root 1 0 R\n>>' + b'x' * 1024  # Add extra data to ensure >1KB
        pdf_file1 = SimpleUploadedFile("John_Doe_Resume.pdf", pdf_content1, content_type="application/pdf")

        # Upload first file
        response1 = self.client.post(self.upload_url, {'resume_files': [pdf_file1]}, format='multipart')
        response_data1 = json.loads(response1.content)
        self.assertTrue(response_data1['success'])
        self.assertEqual(response_data1['results'][0]['status'], 'success')

        # Create second file with same name pattern, with sufficient size (>1KB)
        pdf_content2 = b'%PDF-1.4\n2 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Size 2\n/Root 2 0 R\n>>' + b'y' * 1024  # Add extra data to ensure >1KB
        pdf_file2 = SimpleUploadedFile("John_Doe_CV.pdf", pdf_content2, content_type="application/pdf")
        
        response2 = self.client.post(self.upload_url, {'resume_files': [pdf_file2]}, format='multipart')
        response_data2 = json.loads(response2.content)
        self.assertTrue(response_data2['success'])
        # Should detect it as duplicate by name
        self.assertEqual(response_data2['results'][0]['status'], 'duplicate')