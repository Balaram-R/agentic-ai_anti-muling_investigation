import tkinter as tk

from app.gui.investigation import InvestigationWindow
from app.gui.transaction_visuals import TransactionVisualsWindow


class HumanReviewWorkspace(InvestigationWindow):
    """
    Showcase AML investigator workspace.

    Does not modify the existing InvestigationWindow.
    Owns its own investigation polling so the case is not lost
    when the investigation moves from OPEN to IN_PROGRESS.
    """

    def __init__(self, root, api, investigation_id=None):
        self.transaction_visual_window = None
        super().__init__(root, api, investigation_id)

    def load_case(self):
        try:
            # If we already know the investigation, NEVER rediscover it
            # through the queue. This keeps the same case during review.
            if self.investigation_id is None:
                investigations = self.api.investigations()

                if not investigations:
                    self.show_waiting_screen()
                    self.schedule_refresh()
                    return

                self.investigation_id = investigations[0]["investigation_id"]
                self.analysis_started = False
                self.last_case_signature = None

            case = self.api.investigation_case(
                self.investigation_id
            )

            # Run the AI once for a new investigation.
            if (
                case.get("agent_analysis") is None
                and not self.analysis_started
            ):
                self.analysis_started = True
                self.status.set(
                    "New AML investigation detected. "
                    "Running investigation agents..."
                )

                try:
                    self.api.run_investigation(
                        self.investigation_id
                    )

                    case = self.api.investigation_case(
                        self.investigation_id
                    )

                except RuntimeError:
                    self.analysis_started = False
                    raise

            signature = repr(case)

            if signature != self.last_case_signature:
                self.case = case
                self.last_case_signature = signature
                self.build_ui()

            self.schedule_refresh()

        except RuntimeError as e:
            self.status.set(str(e))
            self.schedule_refresh()

    def start_review(self):
        # Use the existing investigation review behavior.
        super().start_review()

        if self.investigation_id is None:
            return

        if (
            self.transaction_visual_window is None
            or not self.transaction_visual_window.winfo_exists()
        ):
            self.transaction_visual_window = tk.Toplevel(
                self.root
            )

            TransactionVisualsWindow(
                self.transaction_visual_window,
                self.api,
                investigation_id=self.investigation_id,
            )

            self.transaction_visual_window.geometry(
                "1250x850+300+80"
            )

        else:
            self.transaction_visual_window.lift()
            self.transaction_visual_window.focus_force()
