import{a as _}from"./chunk-SRH65J3K.js";import{A as f,C as E,Ca as G,D as v,J as m,Q as g,R as x,T as R,U as V,ba as w,ca as u,da as T,ea as q,h as y,ha as F,j as I,ja as L,ka as j,l as b,m as N,qa as k,s as o,sa as P,t as p,u as l,ua as D,v as a,va as O,wa as h,xa as M,y as n,z as r,za as U}from"./chunk-YTAQRA7X.js";var J=(()=>{let t=class t{constructor(d,s){this.router=d,this.accountService=s,this.accountService.userValue&&this.router.navigate(["/"])}};t.\u0275fac=function(s){return new(s||t)(p(h),p(_))},t.\u0275cmp=b({type:t,selectors:[["ng-component"]],decls:2,vars:0,consts:[[1,"container","col-md-6","offset-md-3","mt-5"]],template:function(s,i){s&1&&(n(0,"div",0),f(1,"router-outlet"),r())},dependencies:[O],encapsulation:2});let e=t;return e})();var K=e=>({"is-invalid":e});function ee(e,t){e&1&&(n(0,"div"),m(1,"Username is required"),r())}function te(e,t){if(e&1&&(n(0,"div",12),l(1,ee,2,0,"div",13),r()),e&2){let c=v();o(),a("ngIf",c.f.username.errors.required)}}function ie(e,t){e&1&&(n(0,"div"),m(1,"Password is required"),r())}function re(e,t){if(e&1&&(n(0,"div",12),l(1,ie,2,0,"div",13),r()),e&2){let c=v();o(),a("ngIf",c.f.password.errors.required)}}function ne(e,t){e&1&&f(0,"span",14)}var Q=(()=>{let t=class t{constructor(d,s,i,C,B){this.formBuilder=d,this.route=s,this.router=i,this.accountService=C,this.alertService=B,this.loading=!1,this.submitted=!1}ngOnInit(){this.form=this.formBuilder.group({username:["",u.required],password:["",u.required]})}get f(){return this.form.controls}onSubmit(){this.submitted=!0,this.alertService.clear(),!this.form.invalid&&(this.loading=!0,console.clear(),console.log("in onsubmit of login component"),this.accountService.login(this.f.username.value,this.f.password.value).pipe(y()).subscribe({next:()=>{let d=this.route.snapshot.queryParams.returnUrl||"/";this.router.navigateByUrl(d)},error:d=>{this.alertService.error(d),this.loading=!1}}))}};t.\u0275fac=function(s){return new(s||t)(p(k),p(D),p(h),p(_),p(G))},t.\u0275cmp=b({type:t,selectors:[["ng-component"]],decls:21,vars:11,consts:[[1,"card"],[1,"card-header"],[1,"card-body"],[3,"ngSubmit","formGroup"],[1,"mb-3"],[1,"form-label"],["type","text","formControlName","username",1,"form-control",3,"ngClass"],["class","invalid-feedback",4,"ngIf"],["type","password","formControlName","password",1,"form-control",3,"ngClass"],[1,"btn","btn-primary",3,"disabled"],["class","spinner-border spinner-border-sm me-1",4,"ngIf"],["routerLink","../register",1,"btn","btn-link"],[1,"invalid-feedback"],[4,"ngIf"],[1,"spinner-border","spinner-border-sm","me-1"]],template:function(s,i){s&1&&(n(0,"div",0)(1,"h4",1),m(2,"Login"),r(),n(3,"div",2)(4,"form",3),E("ngSubmit",function(){return i.onSubmit()}),n(5,"div",4)(6,"label",5),m(7,"Username"),r(),f(8,"input",6),l(9,te,2,1,"div",7),r(),n(10,"div",4)(11,"label",5),m(12,"Password"),r(),f(13,"input",8),l(14,re,2,1,"div",7),r(),n(15,"div")(16,"button",9),l(17,ne,1,0,"span",10),m(18," Login "),r(),n(19,"a",11),m(20,"Not a user yet? Register here"),r()()()()()),s&2&&(o(4),a("formGroup",i.form),o(4),a("ngClass",g(7,K,i.submitted&&i.f.username.errors)),o(),a("ngIf",i.submitted&&i.f.username.errors),o(4),a("ngClass",g(9,K,i.submitted&&i.f.password.errors)),o(),a("ngIf",i.submitted&&i.f.password.errors),o(2),a("disabled",i.loading),o(),a("ngIf",i.loading))},dependencies:[x,R,F,w,T,q,L,j,M],encapsulation:2});let e=t;return e})();var S=e=>({"is-invalid":e});function oe(e,t){e&1&&(n(0,"div"),m(1,"First Name is required"),r())}function ae(e,t){if(e&1&&(n(0,"div",15),l(1,oe,2,0,"div",16),r()),e&2){let c=v();o(),a("ngIf",c.f.firstName.errors.required)}}function se(e,t){e&1&&(n(0,"div"),m(1,"Last Name is required"),r())}function me(e,t){if(e&1&&(n(0,"div",15),l(1,se,2,0,"div",16),r()),e&2){let c=v();o(),a("ngIf",c.f.lastName.errors.required)}}function de(e,t){e&1&&(n(0,"div"),m(1,"E-mail is required"),r())}function le(e,t){if(e&1&&(n(0,"div",15),l(1,de,2,0,"div",16),r()),e&2){let c=v();o(),a("ngIf",c.f.email.errors.required)}}function pe(e,t){e&1&&(n(0,"div"),m(1,"Username is required"),r())}function ce(e,t){if(e&1&&(n(0,"div",15),l(1,pe,2,0,"div",16),r()),e&2){let c=v();o(),a("ngIf",c.f.username.errors.required)}}function fe(e,t){e&1&&(n(0,"div"),m(1,"Password is required"),r())}function ue(e,t){e&1&&(n(0,"div"),m(1,"Password must be at least 6 characters"),r())}function ve(e,t){if(e&1&&(n(0,"div",15),l(1,fe,2,0,"div",16)(2,ue,2,0,"div",16),r()),e&2){let c=v();o(),a("ngIf",c.f.password.errors.required),o(),a("ngIf",c.f.password.errors.minlength)}}function ge(e,t){e&1&&f(0,"span",17)}var W=(()=>{let t=class t{constructor(d,s,i,C,B){this.formBuilder=d,this.route=s,this.router=i,this.accountService=C,this.alertService=B,this.loading=!1,this.submitted=!1}ngOnInit(){this.form=this.formBuilder.group({firstName:["",u.required],lastName:["",u.required],email:["",u.required],username:["",u.required],password:["",[u.required,u.minLength(6)]]})}get f(){return this.form.controls}onSubmit(){this.submitted=!0,this.alertService.clear(),!this.form.invalid&&(this.loading=!0,this.accountService.register(this.form.value).pipe(y()).subscribe({next:()=>{this.alertService.success("Registration successful",{keepAfterRouteChange:!0}),this.router.navigate(["../login"],{relativeTo:this.route})},error:d=>{this.alertService.error(d),this.loading=!1}}))}};t.\u0275fac=function(s){return new(s||t)(p(k),p(D),p(h),p(_),p(G))},t.\u0275cmp=b({type:t,selectors:[["ng-component"]],decls:36,vars:23,consts:[[1,"card"],[1,"card-header"],[1,"card-body"],[3,"ngSubmit","formGroup"],[1,"mb-3"],[1,"form-label"],["type","text","formControlName","firstName",1,"form-control",3,"ngClass"],["class","invalid-feedback",4,"ngIf"],["type","text","formControlName","lastName",1,"form-control",3,"ngClass"],["type","email","formControlName","email",1,"form-control",3,"ngClass"],["type","text","formControlName","username",1,"form-control",3,"ngClass"],["type","password","formControlName","password",1,"form-control",3,"ngClass"],[1,"btn","btn-primary",3,"disabled"],["class","spinner-border spinner-border-sm me-1",4,"ngIf"],["routerLink","../login",1,"btn","btn-link"],[1,"invalid-feedback"],[4,"ngIf"],[1,"spinner-border","spinner-border-sm","me-1"]],template:function(s,i){s&1&&(n(0,"div",0)(1,"h4",1),m(2,"Register"),r(),n(3,"div",2)(4,"form",3),E("ngSubmit",function(){return i.onSubmit()}),n(5,"div",4)(6,"label",5),m(7,"First Name"),r(),f(8,"input",6),l(9,ae,2,1,"div",7),r(),n(10,"div",4)(11,"label",5),m(12,"Last Name"),r(),f(13,"input",8),l(14,me,2,1,"div",7),r(),n(15,"div",4)(16,"label",5),m(17,"E-mail"),r(),f(18,"input",9),l(19,le,2,1,"div",7),r(),n(20,"div",4)(21,"label",5),m(22,"Username"),r(),f(23,"input",10),l(24,ce,2,1,"div",7),r(),n(25,"div",4)(26,"label",5),m(27,"Password"),r(),f(28,"input",11),l(29,ve,3,2,"div",7),r(),n(30,"div")(31,"button",12),l(32,ge,1,0,"span",13),m(33," Register "),r(),n(34,"a",14),m(35,"Cancel"),r()()()()()),s&2&&(o(4),a("formGroup",i.form),o(4),a("ngClass",g(13,S,i.submitted&&i.f.firstName.errors)),o(),a("ngIf",i.submitted&&i.f.firstName.errors),o(4),a("ngClass",g(15,S,i.submitted&&i.f.lastName.errors)),o(),a("ngIf",i.submitted&&i.f.lastName.errors),o(4),a("ngClass",g(17,S,i.submitted&&i.f.email.errors)),o(),a("ngIf",i.submitted&&i.f.email.errors),o(4),a("ngClass",g(19,S,i.submitted&&i.f.username.errors)),o(),a("ngIf",i.submitted&&i.f.username.errors),o(4),a("ngClass",g(21,S,i.submitted&&i.f.password.errors)),o(),a("ngIf",i.submitted&&i.f.password.errors),o(2),a("disabled",i.loading),o(),a("ngIf",i.loading))},dependencies:[x,R,F,w,T,q,L,j,M],encapsulation:2});let e=t;return e})();var be=[{path:"",component:J,children:[{path:"login",component:Q},{path:"register",component:W}]}],X=(()=>{let t=class t{};t.\u0275fac=function(s){return new(s||t)},t.\u0275mod=N({type:t}),t.\u0275inj=I({imports:[U.forChild(be),U]});let e=t;return e})();var Be=(()=>{let t=class t{};t.\u0275fac=function(s){return new(s||t)},t.\u0275mod=N({type:t}),t.\u0275inj=I({imports:[V,P,X]});let e=t;return e})();export{Be as AccountModule};