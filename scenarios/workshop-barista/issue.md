## Contexto

Queremos enviar incidencias de Barista Incidents a una API de un proveedor mediante un trabajo programado. El proveedor entrega una clave de API y permite rotarla. Una persona administradora debe poder configurarla y sustituirla desde la configuración de ventas. La app se usa en más de una empresa.

La extensión ya añade «BRI Incident Nos.» a la configuración de ventas. Todavía no se ha decidido si todas las empresas utilizarán la misma cuenta del proveedor.

## Decisión pendiente

¿Cómo deberíamos guardar la credencial y ponerla a disposición del proceso de envío? Queremos una propuesta de diseño antes de abrir una PR. El proceso debe poder seguir funcionando después de cerrar la sesión de la persona que configuró la integración.
