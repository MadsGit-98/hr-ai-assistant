from django.test import TestCase
from django.core.exceptions import ValidationError
from jobs.models import Applicant
import tempfile
import os


class ResumeApplicantModelTest(TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        self.temp_file.write(b'test content')
        self.temp_file.close()

    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.temp_file.name)

    def test_resume_applicant_creation(self):
        """Test creating a resume applicant with valid data"""
        applicant = Applicant.objects.create(
            applicant_name="John Doe",
            resume_file=self.temp_file.name,
            content_hash="z" * 64,  # 64 character hash - using 'z' to avoid conflicts with other tests
            file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
            file_format="PDF"
        )
        
        self.assertEqual(applicant.applicant_name, "John Doe")
        self.assertTrue(applicant.resume_file.name.endswith('.pdf'))
        self.assertEqual(applicant.content_hash, "z" * 64)
        self.assertEqual(applicant.file_size, 2000)
        self.assertEqual(applicant.file_format, "PDF")
        self.assertEqual(applicant.processing_status, "pending")

    def test_file_format_validation(self):
        """Test that only PDF and DOCX formats are allowed"""
        with self.assertRaises(ValidationError):
            applicant = Applicant(
                applicant_name="John Doe",
                resume_file=self.temp_file.name,
                content_hash="a" * 64,
                file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                file_format="TXT"
            )
            applicant.full_clean()

        # Valid formats should work
        valid_formats = ["PDF", "DOCX"]
        for i, fmt in enumerate(valid_formats):
            applicant = Applicant(
                applicant_name="John Doe",
                resume_file=self.temp_file.name,
                content_hash=chr(ord('a') + i) * 64,  # Use different hash for each format ('a'*64, 'b'*64, etc.)
                file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                file_format=fmt
            )
            try:
                applicant.full_clean()
                applicant.save()
                self.assertEqual(applicant.file_format, fmt)
            except ValidationError:
                self.fail(f"Valid format {fmt} raised ValidationError")

    def test_file_size_validation(self):
        """Test file size constraints (1KB to 10MB)"""
        # Test with a file size that's too small (less than 1KB)
        with self.assertRaises(ValidationError):
            applicant = Applicant(
                applicant_name="John Doe",
                resume_file=self.temp_file.name,
                content_hash="a" * 64,
                file_size=500,  # 500 bytes is less than 1KB
                file_format="PDF"
            )
            applicant.full_clean()

        # Test with a file size that's too large (more than 10MB)
        with self.assertRaises(ValidationError):
            applicant = Applicant(
                applicant_name="John Doe",
                resume_file=self.temp_file.name,
                content_hash="a" * 64,
                file_size=11 * 1024 * 1024,  # 11MB is more than 10MB
                file_format="PDF"
            )
            applicant.full_clean()

        # Test with valid file size (within 1KB to 10MB)
        applicant = Applicant(
            applicant_name="John Doe",
            resume_file=self.temp_file.name,
            content_hash="a" * 64,
            file_size=5000,  # 5KB is within range
            file_format="PDF"
        )
        try:
            applicant.full_clean()
            applicant.save()
        except ValidationError:
            self.fail("Valid file size raised ValidationError")

    def test_required_fields_validation(self):
        """Test that required fields cannot be empty"""
        # Test without applicant name
        with self.assertRaises(ValidationError):
            applicant = Applicant(
                resume_file=self.temp_file.name,
                content_hash="c" * 64,  # Use a different hash
                file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                file_format="PDF"
            )
            applicant.applicant_name = ""
            applicant.full_clean()

        # Test without content hash
        with self.assertRaises(ValidationError):
            applicant = Applicant(
                applicant_name="John Doe",
                resume_file=self.temp_file.name,
                content_hash="d" * 64,  # Need to provide a hash since it's required
                file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                file_format="PDF"
            )
            applicant.content_hash = ""
            applicant.full_clean()

        # Test without resume file
        with self.assertRaises(ValidationError):
            applicant = Applicant(
                applicant_name="John Doe",
                content_hash="a" * 64,
                file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                file_format="PDF"
            )
            # applicant.resume_file = None  # Can't easily test this way
            # Test by trying to create without resume_file if possible
            applicant.full_clean()

    def test_name_format_validation(self):
        """Test that applicant names follow standard name patterns"""
        # Valid names should work
        valid_names = ["John Doe", "Mary-Jane Smith", "O'Connor", "Jean-Luc Picard"]
        for i, name in enumerate(valid_names):
            applicant = Applicant(
                applicant_name=name,
                resume_file=self.temp_file.name,
                content_hash=chr(ord('a') + i) * 64,  # Use different hash for each name
                file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                file_format="PDF"
            )
            try:
                applicant.full_clean()
                applicant.save()
                self.assertEqual(applicant.applicant_name, name)
            except ValidationError:
                self.fail(f"Valid name {name} raised ValidationError")

        # Invalid names (with special characters like @, #, $) should not work
        invalid_names = ["John@Doe", "Mary#Smith", "O'Connor$Test"]
        for name in invalid_names:
            with self.assertRaises(ValidationError):
                applicant = Applicant(
                    applicant_name=name,
                    resume_file=self.temp_file.name,
                    content_hash="a" * 64,
                    file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                    file_format="PDF"
                )
                applicant.full_clean()

    def test_content_hash_unique_constraint(self):
        """Test that content hash must be unique"""
        # Create first applicant
        applicant1 = Applicant.objects.create(
            applicant_name="John Doe",
            resume_file=self.temp_file.name,
            content_hash="x" * 64,  # Use 'x' hash for first applicant
            file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
            file_format="PDF"
        )

        # Try to create another with same content hash (should fail)
        with self.assertRaises(ValidationError):
            applicant2 = Applicant(
                applicant_name="Jane Doe",
                resume_file=self.temp_file.name,  # Different file but same hash
                content_hash="x" * 64,  # Same hash as applicant1
                file_size=2000,  # Use 2KB to satisfy the 1KB minimum requirement
                file_format="PDF"
            )
            applicant2.full_clean()
            applicant2.save()  # This should raise an IntegrityError when saved