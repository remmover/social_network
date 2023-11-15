"""Authentication and Account-related"""
INVALID_TOKEN = "Invalid token for email verification"
INVALID_SCOPE_TOKEN = "Invalid scope for token"
VALIDATE_CREDENTIALS = "Could not validate credentials"
ACCOUNT_EXIST = "Account already exists"
INVALID_EMAIL = "Invalid email"
EMAIL_NOT_CONFIRMED = "Email not confirmed"
BAD_PASSWORD = "Invalid password"
INVALID_REFRESH_TOKEN = "Invalid refresh token"
INVALID_CONFIRMATION_TOKEN = "Verification error"
EMAIL_ALREADY_CONFIRMED = "Your email is already confirmed"
EMAIL_CONFIRMED = "Email confirmed"
CHECK_EMAIL_CONFIRMED = "Check your email for confirmation."
PASSWORD_RESET_ERROR = "Password reset error"
PASSWORD_RESET_EMAIL_SUCCESS = "Email for reset password sent successfully"
PASSWORD_RESET_SUCCESS = "Password reset successfully"
USER_NOT_FOUND = "User not found"
NO_ACCESS = "Access denied"


"""Access Control and Authorization"""
NOT_ACCESS_ANALYTICS = "Unauthorized access: User does not own the post."


"""Posts and Likes"""
POST_NOT_FOUND = "Post not found"
ALREADY_LIKED = "User has already liked this post"
ALREADY_UNLIKED = "User has already unliked this post"
POST_EXISTS = "Post already exists"


"""Date and Image-related"""
INVALID_DATE_RANGE = "date_from must be before date_to"
IMAGE_ERROR = "Image not found or doesn't belong to the current user"


"""Comments"""
COMMENT_UPDATED = "Comment description is successfully changed."
COMMENT_NOT_FOUND = "Comment not found or doesn't belong to the current user"
