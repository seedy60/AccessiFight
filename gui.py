"""wxPython setup wizard and settings dialog for AccessiFight."""

import sys
import threading
import wx

from config import load_config, save_config


class SetupWizard(wx.Dialog):
    """First-launch setup wizard and settings dialog."""

    def __init__(self, parent=None):
        super().__init__(parent, title="AccessiFight Setup", size=(520, 480),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.cfg = load_config()
        self._build_ui()
        self.Centre()

    def _build_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(panel, label="Welcome to AccessiFight!"),
                   0, wx.ALL, 10)

        # --- Speech output ---
        self.speech_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Speech Output")

        self.rb_screen_reader = wx.RadioButton(panel, label="Screen reader", style=wx.RB_GROUP)
        self.rb_sapi5 = wx.RadioButton(panel, label="SAPI 5")
        self.speech_box.Add(self.rb_screen_reader, 0, wx.ALL, 4)
        self.speech_box.Add(self.rb_sapi5, 0, wx.ALL, 4)

        voice_row = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_sapi_voice = wx.StaticText(panel, label="Voice:")
        self.sapi_voice_choice = wx.Choice(panel, choices=[])
        voice_row.Add(self.lbl_sapi_voice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        voice_row.Add(self.sapi_voice_choice, 1)
        self.speech_box.Add(voice_row, 0, wx.EXPAND | wx.ALL, 4)

        sizer.Add(self.speech_box, 0, wx.EXPAND | wx.ALL, 5)

        # Populate SAPI 5 voices
        from tts import list_sapi5_voices
        self._sapi_voices = list_sapi5_voices()
        for v in self._sapi_voices:
            self.sapi_voice_choice.Append(v)
        saved_voice = self.cfg.get("sapi5_voice", "")
        if saved_voice in self._sapi_voices:
            self.sapi_voice_choice.SetStringSelection(saved_voice)
        elif self._sapi_voices:
            self.sapi_voice_choice.SetSelection(0)

        if self.cfg.get("speech_output") == "sapi5":
            self.rb_sapi5.SetValue(True)
        else:
            self.rb_screen_reader.SetValue(True)

        # --- Description method ---
        sizer.Add(wx.StaticText(panel, label="Choose how screenshots are described:"),
                   0, wx.LEFT | wx.RIGHT, 10)

        self.rb_ocr = wx.RadioButton(panel, label="Offline OCR (Tesseract)", style=wx.RB_GROUP)
        self.rb_gemini = wx.RadioButton(panel, label="Google Gemini")
        self.rb_cloudflare = wx.RadioButton(panel, label="Cloudflare Workers AI")

        sizer.Add(self.rb_ocr, 0, wx.ALL, 5)
        sizer.Add(self.rb_gemini, 0, wx.ALL, 5)
        sizer.Add(self.rb_cloudflare, 0, wx.ALL, 5)

        # --- OCR options ---
        self.ocr_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "OCR Settings")
        self.ocr_box.Add(wx.StaticText(panel, label="Tesseract path (leave blank for default):"),
                         0, wx.ALL, 4)
        self.txt_tesseract = wx.TextCtrl(panel, value=self.cfg.get("tesseract_path", ""))
        self.ocr_box.Add(self.txt_tesseract, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(self.ocr_box, 0, wx.EXPAND | wx.ALL, 5)

        # --- Gemini options ---
        self.gemini_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Gemini Settings")
        self.gemini_box.Add(wx.StaticText(panel, label="API Key:"), 0, wx.ALL, 4)
        self.txt_gemini_key = wx.TextCtrl(panel, value=self.cfg.get("gemini_api_key", ""),
                                           style=wx.TE_PASSWORD)
        self.gemini_box.Add(self.txt_gemini_key, 0, wx.EXPAND | wx.ALL, 4)

        model_row = wx.BoxSizer(wx.HORIZONTAL)
        self.gemini_model_choice = wx.Choice(panel, choices=[])
        self.btn_gemini_list = wx.Button(panel, label="List Models")
        model_row.Add(wx.StaticText(panel, label="Model:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        model_row.Add(self.gemini_model_choice, 1, wx.RIGHT, 5)
        model_row.Add(self.btn_gemini_list, 0)
        self.gemini_box.Add(model_row, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(self.gemini_box, 0, wx.EXPAND | wx.ALL, 5)

        # --- Cloudflare options ---
        self.cf_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Cloudflare Workers AI Settings")
        self.cf_box.Add(wx.StaticText(panel, label="Account ID:"), 0, wx.ALL, 4)
        self.txt_cf_account = wx.TextCtrl(panel, value=self.cfg.get("cloudflare_account_id", ""))
        self.cf_box.Add(self.txt_cf_account, 0, wx.EXPAND | wx.ALL, 4)

        self.cf_box.Add(wx.StaticText(panel, label="API Token:"), 0, wx.ALL, 4)
        self.txt_cf_token = wx.TextCtrl(panel, value=self.cfg.get("cloudflare_api_token", ""),
                                         style=wx.TE_PASSWORD)
        self.cf_box.Add(self.txt_cf_token, 0, wx.EXPAND | wx.ALL, 4)

        from describe import CLOUDFLARE_VISION_MODELS
        cf_model_row = wx.BoxSizer(wx.HORIZONTAL)
        cf_choices = list(CLOUDFLARE_VISION_MODELS) + ["Custom"]
        self.cf_model_choice = wx.Choice(panel, choices=cf_choices)
        cf_model_row.Add(wx.StaticText(panel, label="Model:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        cf_model_row.Add(self.cf_model_choice, 1)
        self.cf_box.Add(cf_model_row, 0, wx.EXPAND | wx.ALL, 4)

        self.lbl_cf_custom = wx.StaticText(panel, label="Custom model:")
        self.txt_cf_custom_model = wx.TextCtrl(panel)
        self.cf_box.Add(self.lbl_cf_custom, 0, wx.ALL, 4)
        self.cf_box.Add(self.txt_cf_custom_model, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(self.cf_box, 0, wx.EXPAND | wx.ALL, 5)

        # Save button
        self.btn_save = wx.Button(panel, label="Save && Start")
        sizer.Add(self.btn_save, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(sizer)

        # Pre-select current method
        method = self.cfg.get("method", "")
        if method == "gemini":
            self.rb_gemini.SetValue(True)
        elif method == "cloudflare":
            self.rb_cloudflare.SetValue(True)
        else:
            self.rb_ocr.SetValue(True)

        # Prepopulate model choices
        saved_gemini = self.cfg.get("gemini_model", "")
        if saved_gemini:
            self.gemini_model_choice.Append(saved_gemini)
            self.gemini_model_choice.SetSelection(0)

        saved_cf = self.cfg.get("cloudflare_model", "")
        if saved_cf in CLOUDFLARE_VISION_MODELS:
            self.cf_model_choice.SetStringSelection(saved_cf)
        elif saved_cf:
            self.cf_model_choice.SetStringSelection("Custom")
            self.txt_cf_custom_model.SetValue(saved_cf)
        else:
            self.cf_model_choice.SetSelection(0)

        self._update_visibility()

        # Bind events
        self.rb_screen_reader.Bind(wx.EVT_RADIOBUTTON, self._on_speech_change)
        self.rb_sapi5.Bind(wx.EVT_RADIOBUTTON, self._on_speech_change)
        self.rb_ocr.Bind(wx.EVT_RADIOBUTTON, self._on_method_change)
        self.rb_gemini.Bind(wx.EVT_RADIOBUTTON, self._on_method_change)
        self.rb_cloudflare.Bind(wx.EVT_RADIOBUTTON, self._on_method_change)
        self.cf_model_choice.Bind(wx.EVT_CHOICE, self._on_cf_model_change)
        self.btn_gemini_list.Bind(wx.EVT_BUTTON, self._on_list_gemini)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)

    def _get_selected_method(self) -> str:
        if self.rb_gemini.GetValue():
            return "gemini"
        if self.rb_cloudflare.GetValue():
            return "cloudflare"
        return "ocr"

    def _on_speech_change(self, event):
        self._update_visibility()

    def _on_method_change(self, event):
        self._update_visibility()

    def _on_cf_model_change(self, event):
        self._update_visibility()

    def _update_visibility(self):
        method = self._get_selected_method()
        is_sapi = self.rb_sapi5.GetValue()

        # SAPI voice selector
        self.lbl_sapi_voice.Show(is_sapi)
        self.sapi_voice_choice.Show(is_sapi)

        # Description method boxes
        self.ocr_box.ShowItems(method == "ocr")
        self.ocr_box.GetStaticBox().Show(method == "ocr")

        self.gemini_box.ShowItems(method == "gemini")
        self.gemini_box.GetStaticBox().Show(method == "gemini")

        self.cf_box.ShowItems(method == "cloudflare")
        self.cf_box.GetStaticBox().Show(method == "cloudflare")

        # Custom model field within Cloudflare
        if method == "cloudflare":
            is_custom = self.cf_model_choice.GetStringSelection() == "Custom"
            self.lbl_cf_custom.Show(is_custom)
            self.txt_cf_custom_model.Show(is_custom)

        self.GetChildren()[0].Layout()
        self.Fit()

    def _on_list_gemini(self, event):
        api_key = self.txt_gemini_key.GetValue().strip()
        if not api_key:
            wx.MessageBox("Enter a Gemini API key first.", "Error", wx.OK | wx.ICON_ERROR)
            return
        self.btn_gemini_list.Disable()
        self.btn_gemini_list.SetLabel("Loading...")

        def fetch():
            try:
                from describe import list_gemini_models
                models = list_gemini_models(api_key)
                wx.CallAfter(self._populate_gemini_models, models)
            except Exception as e:
                wx.CallAfter(wx.MessageBox, f"Failed to list models: {e}", "Error",
                             wx.OK | wx.ICON_ERROR)
            finally:
                wx.CallAfter(self.btn_gemini_list.Enable)
                wx.CallAfter(self.btn_gemini_list.SetLabel, "List Models")

        threading.Thread(target=fetch, daemon=True).start()

    def _populate_gemini_models(self, models: list[str]):
        self.gemini_model_choice.Clear()
        for m in models:
            self.gemini_model_choice.Append(m)
        saved = self.cfg.get("gemini_model", "")
        if saved in models:
            self.gemini_model_choice.SetStringSelection(saved)
        elif models:
            self.gemini_model_choice.SetSelection(0)

    def _on_save(self, event):
        method = self._get_selected_method()
        self.cfg["method"] = method
        self.cfg["speech_output"] = "sapi5" if self.rb_sapi5.GetValue() else "screen_reader"

        sel = self.sapi_voice_choice.GetSelection()
        if sel != wx.NOT_FOUND:
            self.cfg["sapi5_voice"] = self.sapi_voice_choice.GetString(sel)

        self.cfg["tesseract_path"] = self.txt_tesseract.GetValue().strip()
        self.cfg["gemini_api_key"] = self.txt_gemini_key.GetValue().strip()
        self.cfg["cloudflare_account_id"] = self.txt_cf_account.GetValue().strip()
        self.cfg["cloudflare_api_token"] = self.txt_cf_token.GetValue().strip()

        sel = self.gemini_model_choice.GetSelection()
        if sel != wx.NOT_FOUND:
            self.cfg["gemini_model"] = self.gemini_model_choice.GetString(sel)

        sel = self.cf_model_choice.GetSelection()
        if sel != wx.NOT_FOUND:
            chosen = self.cf_model_choice.GetString(sel)
            if chosen == "Custom":
                custom = self.txt_cf_custom_model.GetValue().strip()
                if custom:
                    self.cfg["cloudflare_model"] = custom
            else:
                self.cfg["cloudflare_model"] = chosen

        self.cfg["setup_complete"] = True
        save_config(self.cfg)
        self.EndModal(wx.ID_OK)


def show_setup_wizard(parent=None) -> bool:
    """Show the setup wizard. Returns True if user completed setup."""
    dlg = SetupWizard(parent)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result == wx.ID_OK


def show_settings(parent=None) -> bool:
    """Show settings dialog (reuses the same wizard UI). Returns True if saved."""
    dlg = SetupWizard(parent)
    dlg.SetTitle("AccessiFight Settings")
    dlg.btn_save.SetLabel("Save")
    result = dlg.ShowModal()
    dlg.Destroy()
    return result == wx.ID_OK
