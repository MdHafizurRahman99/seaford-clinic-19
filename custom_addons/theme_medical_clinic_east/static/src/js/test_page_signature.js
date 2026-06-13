import { SignatureDialog } from "@web/core/signature/signature_dialog";
import { useService } from "@web/core/utils/hooks";
import { mountComponent } from "@web/env";
import publicWidget from "@web/legacy/js/public/public_widget";

import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";

class TestPageSignatureField extends Component {
    static template = "theme_medical_clinic_east.TestPageSignatureField";
    static props = {
        fullNameInputId: String,
    };

    setup() {
        this.dialog = useService("dialog");
        this.rootRef = useRef("root");
        this.state = useState({
            error: "",
            signatureImage: "",
            signatureName: "",
        });

        onMounted(() => {
            this.formEl = this.rootRef.el.closest("form");
            this.boundSubmitHandler = this.onFormSubmit.bind(this);
            this.formEl?.addEventListener("submit", this.boundSubmitHandler);
        });

        onWillUnmount(() => {
            this.formEl?.removeEventListener("submit", this.boundSubmitHandler);
        });
    }

    get fullNameInput() {
        return document.getElementById(this.props.fullNameInputId);
    }

    clearSignature() {
        this.state.signatureImage = "";
        this.state.signatureName = "";
        this.state.error = "";
    }

    openSignatureDialog() {
        const defaultName = this.fullNameInput?.value.trim() || this.state.signatureName || "";
        this.state.error = "";

        this.dialog.add(SignatureDialog, {
            defaultName,
            nameAndSignatureProps: {
                defaultFont: "LaBelleAurore-Regular.ttf",
                displaySignatureRatio: 3,
                mode: defaultName ? "auto" : "draw",
                noInputName: false,
                signatureType: "signature",
            },
            uploadSignature: ({ name, signatureImage }) => {
                this.state.signatureImage = signatureImage;
                this.state.signatureName = name || "";
                this.state.error = "";
                if (name && this.fullNameInput) {
                    this.fullNameInput.value = name;
                }
            },
        });
    }

    onFormSubmit(ev) {
        if (this.state.signatureImage) {
            this.state.error = "";
            return;
        }

        ev.preventDefault();
        this.state.error = "Please create a signature before submitting the form.";
        this.rootRef.el.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    }
}

publicWidget.registry.TestPageSignatureField = publicWidget.Widget.extend({
    selector: ".o_test_page_signature_mount",

    async start() {
        this.component = await mountComponent(TestPageSignatureField, this.el, {
            props: {
                fullNameInputId: this.el.dataset.fullNameInputId,
            },
        });
        return this._super(...arguments);
    },

    destroy() {
        this.component?.destroy();
        return this._super(...arguments);
    },
});

export default publicWidget.registry.TestPageSignatureField;
