/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SchoolDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            error: false,
            metrics: {},
            feeStates: [],
            admissions: [],
        });
        onWillStart(() => this.loadDashboard());
    }

    async loadDashboard() {
        this.state.loading = true;
        this.state.error = false;
        try {
            const [students, enrolledStudents, teachers, pendingAdmissions, feeTotals, feeStates, admissions] = await Promise.all([
                this.orm.searchCount("school.student", []),
                this.orm.searchCount("school.student", [["state", "=", "enrolled"]]),
                this.orm.searchCount("school.teacher", []),
                this.orm.searchCount("school.admission", [["state", "in", ["new", "review"]]]),
                this.orm.call("school.student.fee", "read_group", [[], ["amount_total:sum", "amount_paid:sum", "amount_due:sum"], []]),
                this.orm.call("school.student.fee", "read_group", [[], ["amount_total:sum"], ["state"]]),
                this.orm.searchRead(
                    "school.admission",
                    [],
                    ["name", "student_name", "grade_id", "state", "create_date"],
                    { order: "create_date desc", limit: 5 }
                ),
            ]);
            const totals = feeTotals[0] || {};
            const totalBilled = totals.amount_total || 0;
            this.state.metrics = {
                students,
                enrolledStudents,
                teachers,
                pendingAdmissions,
                totalBilled,
                totalPaid: totals.amount_paid || 0,
                totalDue: totals.amount_due || 0,
            };
            this.state.feeStates = feeStates.map((item) => ({
                label: item.state ? item.state[1] : "Undefined",
                amount: item.amount_total || 0,
                percentage: totalBilled ? Math.round(((item.amount_total || 0) / totalBilled) * 100) : 0,
            }));
            this.state.admissions = admissions;
        } catch (error) {
            console.error("Unable to load school dashboard", error);
            this.state.error = true;
        } finally {
            this.state.loading = false;
        }
    }

    openAction(event) {
        const actionXmlId = event.currentTarget.dataset.action;
        if (actionXmlId) {
            this.action.doAction(actionXmlId);
        }
    }

    formatNumber(value) {
        return new Intl.NumberFormat().format(value || 0);
    }

    formatAmount(value) {
        return new Intl.NumberFormat(undefined, {
            maximumFractionDigits: 0,
            minimumFractionDigits: 0,
        }).format(value || 0);
    }

    getGreeting() {
        const hour = new Date().getHours();
        if (hour < 12) {
            return "Good morning";
        }
        if (hour < 18) {
            return "Good afternoon";
        }
        return "Good evening";
    }

    formatStatus(state) {
        return {
            new: "New",
            review: "Under Review",
            approved: "Approved",
            rejected: "Rejected",
        }[state] || state || "Unknown";
    }
}

SchoolDashboard.template = "SDS_school_management_system.SchoolDashboard";
registry.category("actions").add("school_management_dashboard", SchoolDashboard);
