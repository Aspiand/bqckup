"""Retry wrapper for backup operations with error collection."""
import time
from typing import Callable, Dict, Any
from constant import MAX_RETRIES, BACKOFF
from rich import print


def retry_operation(
    operation: Callable[..., Dict[str, Any]],
    operation_args: Dict[str, Any],
    operation_name: str,
    max_retries: int = MAX_RETRIES,
    backoff: int = BACKOFF,
) -> Dict[str, Any]:
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation: The function to retry
        operation_args: Arguments to pass to the operation
        operation_name: Human-readable name for logging
        max_retries: Maximum number of retry attempts
        backoff: Seconds to wait between retries
    
    Returns:
        Dict with:
        - success: bool - Whether the operation succeeded
        - errors: list[str] - All errors from all attempts
        - **other fields from successful/last attempt
    
    Raises:
        KeyboardInterrupt: Re-raised immediately without retry
    """
    all_errors = []
    result = None
    
    for attempt in range(max_retries):
        try:
            attempt_info = f" (Attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""
            print(f"[green]Starting {operation_name}[/green]{attempt_info}...")

            result = operation(**operation_args)

            if result.get("success"):
                print(f"[green]{operation_name} successful.[/green]")
                # Add collected errors from previous attempts
                if "errors" not in result:
                    result["errors"] = []
                result["errors"].extend(all_errors)
                return result

            # Check if we should stop retrying
            if result.get("should_retry") is False:
                print(f"[yellow]{operation_name} requested no retry.[/yellow]")
                if "errors" not in result:
                    result["errors"] = []
                result["errors"].extend(all_errors)
                return result

            # Operation returned failure
            error = result.get("traceback") or result.get("error")
            if error:
                all_errors.append(str(error))

            error_message = result.get("message", "Unknown error")
            print(f"[yellow]{operation_name} failed: {error_message}[/yellow]")

            if attempt < max_retries - 1:
                print(f"[yellow]Retrying in {backoff} seconds...[/yellow]")
                time.sleep(backoff)

        except KeyboardInterrupt:
            raise # Re-raise immediately, don't retry
        except Exception as e:
            # Unexpected exception during operation
            error_str = str(e)
            all_errors.append(error_str)
            print(f"[yellow]{operation_name} raised exception: {error_str}[/yellow]")
            
            if attempt < max_retries - 1:
                print(f"[yellow]Retrying in {backoff} seconds...[/yellow]")
                time.sleep(backoff)
            else:
                # Last attempt failed
                result = {
                    "success": False,
                    "message": f"{operation_name} failed after {max_retries} attempts",
                    "error": e,
                    "errors": all_errors,
                }
    
    # All retries exhausted
    print(f"[red]{operation_name} failed after {max_retries} attempts.[/red]")

    # Return the last result with all errors
    if result:
        if "errors" not in result:
            result["errors"] = []
        result["errors"].extend(all_errors)
        # Ensure it's properly marked as failed
        result["success"] = False
    else:
        result = {
            "success": False,
            "message": f"{operation_name} failed after {max_retries} attempts",
            "errors": all_errors,
        }

    return result
